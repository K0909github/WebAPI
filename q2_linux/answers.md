# Q2 模範解答（ワンライナー例）

前提：タブ区切りなので `-F '\t'` を使う。

## 1) purchase 行の抽出（ヘッダ維持）

```bash
# 1行目のヘッダは残しつつ、3列目が purchase の行だけを抜き出す
# -F '\t' : 列の区切り文字をタブに設定する
# NR==1    : 1行目(ヘッダ)だけは条件に関係なく出力する
# $3=="purchase" : 3列目が purchase の行を出力する
awk -F '\t' 'NR==1 || $3=="purchase"' events.tsv
```

## 2) user_id ごとの purchase 回数 TOP10

```bash
# 2列目 user_id を purchase 行から取り出し、件数の多い順に上位10件を出す
# 1) awk: ヘッダ以外(NR>1)で、3列目が purchase の行だけを対象にする
# 2) print $2: 2列目 user_id だけを取り出す
# 3) sort: user_id を並べ替えて同一IDを隣り合わせにする
# 4) uniq -c: 連続した同一IDを数えて「件数 ID」の形式にする
# 5) sort -rn: 件数を数値で降順ソートする
# 6) head -n 10: 上位10行だけ出力する
awk -F '\t' 'NR>1 && $3=="purchase"{print $2}' events.tsv | sort | uniq -c | sort -rn | head -n 10
```

## 3) purchase value の合計と平均

```bash
# purchase の4列目 value を足し合わせ、件数で割って平均も出す
# 1) NR>1: ヘッダ以外の行だけ対象
# 2) $3=="purchase": purchase 行だけ対象
# 3) sum+=$4: 4列目 value を合計
# 4) n+=1: 件数カウント
# 5) END: 全行処理後に合計と平均を出力
# 6) n==0: purchase が0件なら「0 0」を出す
awk -F '\t' 'NR>1 && $3=="purchase"{sum+=$4; n+=1} END{if(n==0) print "0 0"; else print sum, sum/n}' events.tsv
```

## 4) gzip 圧縮（events.tsv.gz）対応の形

（例：1)）

```bash
# gzip を先に展開してから、通常の TSV と同じ awk を当てる
# gzip -cd: 圧縮ファイルを標準出力に展開する（ファイルは残る）
# | : 左の出力を右の入力に渡す（パイプ）
# awk ... : 展開されたTSVに対して同じ条件で抽出する
gzip -cd events.tsv.gz | awk -F '\t' 'NR==1 || $3=="purchase"'
```

同様に 2) 3) も先頭に `gzip -cd events.tsv.gz |` を付ける。
