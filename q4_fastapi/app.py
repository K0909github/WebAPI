from __future__ import annotations

import math
import sqlite3
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field

# SQLite の保存先ファイル
# 相対パスなので、このファイルを実行した作業ディレクトリに作られる
DB_PATH = "predictions.db"


# 現在時刻を UTC の ISO 形式で返す
# DB に保存するタイムスタンプはタイムゾーン付きで統一する
def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# 1つの値を 0〜1 に変換するシグモイド関数
# モデルのスコアを確率っぽい値に押し込むために使う
def sigmoid(z: float) -> float:
    # 大きな正負の値でも壊れにくい数値安定版
    # exp のオーバーフローを避けるため、符号で分岐する
    if z >= 0:
        ez = math.exp(-z)
        return 1.0 / (1.0 + ez)
    ez = math.exp(z)
    return ez / (1.0 + ez)


# 2つの特徴量から予測スコアを作る簡単な関数
# 本番のMLモデルの代わりに、固定係数の線形 + シグモイドで代用
def score_fn(x1: float, x2: float) -> float:
    # 固定係数の簡易ロジスティック回帰のイメージ
    # b0 はバイアス、b1/b2 は特徴量の重み
    b0, b1, b2 = -0.2, 1.1, -0.7
    return sigmoid(b0 + b1 * x1 + b2 * x2)


# SQLite への接続を作る
# check_same_thread=False は FastAPI の並行処理で使うための設定
def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


# 起動時に predictions テーブルがなければ作る
# 既に存在する場合は何もしないので冪等
def init_db() -> None:
    conn = get_conn()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                x1 REAL NOT NULL,
                x2 REAL NOT NULL,
                score REAL NOT NULL
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


# /predict に渡す入力形式
# 受け取る JSON の形を Pydantic で定義する
class PredictIn(BaseModel):
    x1: float = Field(..., description="feature 1")
    x2: float = Field(..., description="feature 2")


# /predict の返却形式
# DB に保存した id と計算結果を返す
class PredictOut(BaseModel):
    id: int
    score: float


# FastAPI アプリ本体
# ここで API のタイトルやバージョンを設定する
app = FastAPI(title="Scoring API", version="1.0.0")


# 起動時に DB 初期化を実行する
# テーブルがない状態でも API が動くようにする
@app.on_event("startup")
def _startup() -> None:
    init_db()


# 予測を1件作成して保存する
# ここでスコア計算 → DB insert → 結果返却まで行う
@app.post("/predict", response_model=PredictOut, status_code=201)
def predict(payload: PredictIn) -> PredictOut:
    # NaN や無限大は受け付けない
    # JSON の数値でも NaN/inf は不正とみなす
    if not math.isfinite(payload.x1) or not math.isfinite(payload.x2):
        raise HTTPException(status_code=400, detail="x1/x2 must be finite numbers")

    # 入力からスコアを計算する
    # score_fn は 0〜1 の範囲を返す
    score = float(score_fn(payload.x1, payload.x2))
    created_at = utc_now_iso()

    # DB に保存して採番された id を受け取る
    # lastrowid で SQLite が自動採番した id を取得
    conn = get_conn()
    try:
        cur = conn.execute(
            "INSERT INTO predictions (created_at, x1, x2, score) VALUES (?, ?, ?, ?)",
            (created_at, payload.x1, payload.x2, score),
        )
        conn.commit()
        new_id = int(cur.lastrowid)
    finally:
        conn.close()

    # 保存した id と計算結果を返す
    # score は見やすさのため小数6桁に丸める
    return PredictOut(id=new_id, score=round(score, 6))


# 保存済み予測を新しい順に一覧表示する
# limit は Query で 1〜1000 の範囲に制限
@app.get("/predictions")
def list_predictions(limit: int = Query(100, ge=1, le=1000)):
    conn = get_conn()
    try:
        rows = conn.execute(
            "SELECT id, created_at, x1, x2, score FROM predictions ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


# ID 指定で1件取得する
# 見つからない場合は 404 を返す
@app.get("/predictions/{pred_id}")
def get_prediction(pred_id: int):
    conn = get_conn()
    try:
        row = conn.execute(
            "SELECT id, created_at, x1, x2, score FROM predictions WHERE id = ?",
            (pred_id,),
        ).fetchone()
    finally:
        conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail="Not found")
    return dict(row)


# ID 指定で1件削除する
# 削除できたら 204、対象がなければ 404
@app.delete("/predictions/{pred_id}", status_code=204)
def delete_prediction(pred_id: int):
    conn = get_conn()
    try:
        cur = conn.execute("DELETE FROM predictions WHERE id = ?", (pred_id,))
        conn.commit()
        # 0 件なら対象がなかったので 404 を返す
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Not found")
        return None
    finally:
        conn.close()
