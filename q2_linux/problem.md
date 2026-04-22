# Q2：Linuxコマンド（抽出・集計）

- 制限時間目安：1時間
- テーマ：ログ/TSV から特徴量を作る（awk・sort・uniq）

## 入力ファイル

同一フォルダに `events.tsv` がある。
タブ区切り、ヘッダあり。

カラム：

1. `timestamp`（ISO8601）
2. `user_id`（文字列）
3. `event`（`view` / `click` / `purchase`）
4. `value`（数値。purchase の場合は購入金額のつもり）

## 問題

以下をそれぞれ「ワンライナー（パイプ可）」で実行せよ。

1) `event=purchase` の行だけ抽出せよ（ヘッダは残すこと）

2) `user_id` ごとの `purchase` 回数を数え、回数が多い順に TOP10 を表示せよ（形式は `count user_id` でよい）

3) `purchase` の `value` について、合計と平均を出力せよ（`sum avg` の2つを空白区切りで出せばよい。purchaseが0件なら `0 0`）

4) 追加：入力が `events.tsv.gz`（gzip圧縮）で与えられても 1)〜3) が実行できる形にせよ（例：`gzip -cd ... | ...`）

## 採点観点（簡易）

- 列指定で厳密に処理できている（grep の雰囲気マッチのみになっていない）
- 数値ソート/降順などが適切
- purchase=0件などの端ケースを意識
