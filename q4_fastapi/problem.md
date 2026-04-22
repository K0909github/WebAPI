# Q4：WebAPI（FastAPI + SQLite）

- 制限時間目安：2時間
- テーマ：推論（スコアリング）API + 推論ログ永続化

## 概要

SQLite を使い、推論APIとログ閲覧APIを実装せよ。
推論は簡単な線形 → シグモイドでよい（係数は固定でOK）。

## DB

SQLite を使用し、`predictions` テーブルを作成する。

- `id` integer primary key autoincrement
- `created_at` text（ISO8601）
- `x1` real
- `x2` real
- `score` real（0〜1）

## API仕様

### 1) POST /predict

入力：
```json
{ "x1": 1.2, "x2": -0.7 }
```

出力（成功時 `201`）：
```json
{ "id": 123, "score": 0.731 }
```

要件：
- `x1` / `x2` は有限な数値であること（NaN/inf は `400`）
- 推論結果を必ずDBに保存すること（リクエストごとに1行 insert）

### 2) GET /predictions?limit=100

直近の推論ログを新しい順（id降順）で返す。

- `limit` は 1〜1000、デフォルト 100

### 3) GET /predictions/{id}

1件返す。なければ `404`。

### 4) DELETE /predictions/{id}

削除できたら `204`、なければ `404`。

## 実装制約

- 言語：Python
- フレームワーク：FastAPI（固定）
- DB：sqlite3（標準ライブラリでOK）
- DB初期化は冪等（`CREATE TABLE IF NOT EXISTS`）

## 動作確認（例）

1. 依存導入

```bash
pip install -r requirements.txt
```

2. 起動

```bash
uvicorn app:app --reload
```

3. 疎通（例）

```bash
curl -X POST http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d "{\"x1\":1.2,\"x2\":-0.7}"
curl "http://127.0.0.1:8000/predictions?limit=5"
```
