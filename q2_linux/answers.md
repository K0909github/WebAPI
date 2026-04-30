# Q2 模範解答（ワンライナー例）

前提：タブ区切りなので `-F '\t'` を使う。

## 1) purchase 行の抽出（ヘッダ維持）

```bash
# 1行目のヘッダは残しつつ、3列目が purchase の行だけを抜き出す
awk -F '\t' 'NR==1 || $3=="purchase"' events.tsv
```

## 2) user_id ごとの purchase 回数 TOP10

```bash
# 2列目 user_id を purchase 行から取り出し、件数の多い順に上位10件を出す
awk -F '\t' 'NR>1 && $3=="purchase"{print $2}' events.tsv | sort | uniq -c | sort -rn | head -n 10
```

## 3) purchase value の合計と平均

```bash
# purchase の4列目 value を足し合わせ、件数で割って平均も出す
awk -F '\t' 'NR>1 && $3=="purchase"{sum+=$4; n+=1} END{if(n==0) print "0 0"; else print sum, sum/n}' events.tsv
```

## 4) gzip 圧縮（events.tsv.gz）対応の形

（例：1)）

```bash
# gzip を先に展開してから、通常の TSV と同じ awk を当てる
gzip -cd events.tsv.gz | awk -F '\t' 'NR==1 || $3=="purchase"'
```

同様に 2) 3) も先頭に `gzip -cd events.tsv.gz |` を付ける。
