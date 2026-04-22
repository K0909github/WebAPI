# Q4 FastAPI 実行手順（模範）

## セットアップ

```bash
cd q4_fastapi
pip install -r requirements.txt
```

## 起動

```bash
uvicorn app:app --reload
```

- Swagger UI: http://127.0.0.1:8000/docs

## 動作確認（curl例）

```bash
curl -X POST http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d "{\"x1\":1.2,\"x2\":-0.7}"

curl "http://127.0.0.1:8000/predictions?limit=5"

curl http://127.0.0.1:8000/predictions/1

curl -X DELETE http://127.0.0.1:8000/predictions/1
```

## 期待ポイント

- `POST /predict` は必ず DB に insert し、`201` を返す
- `GET /predictions` は新しい順（id降順）
- `limit` は 1〜1000 の範囲
- 1件取得/削除は存在しない場合 `404`
