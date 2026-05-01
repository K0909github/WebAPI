# Q4 FastAPI 実行手順（模範）

## Docker でのセットアップ

```bash
cd q4_fastapi
docker build -t q4-fastapi .
```

## Docker での起動

```bash
docker run --rm -p 8000:8000 -v ${PWD}:/app q4-fastapi
```

- Swagger UI: http://127.0.0.1:8000/docs

## 動作確認（curl例 / PowerShell）

PowerShell の `curl` は `Invoke-WebRequest` なので、`curl.exe` を使う。
`--%` を付けると PowerShell の解釈を止められて JSON が壊れない。

```bash
curl.exe --% -X POST http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d "{\"x1\":1.2,\"x2\":-0.7}"

curl.exe "http://127.0.0.1:8000/predictions?limit=5"

curl.exe http://127.0.0.1:8000/predictions/1

curl.exe -X DELETE http://127.0.0.1:8000/predictions/1
```

## 期待ポイント

- `POST /predict` は必ず DB に insert し、`201` を返す
- `GET /predictions` は新しい順（id降順）
- `limit` は 1〜1000 の範囲
- 1件取得/削除は存在しない場合 `404`
