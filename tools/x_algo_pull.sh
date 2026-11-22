#!/bin/sh
# X の公開アルゴリズム（オープンソース）から「重みづけ・ランキング」に関する部分を取り出して保存する（週1）
# 本人がやること: なし。AI が実行する。git が要る。
# 保存先: data/x_algo/  （生のコードは保存しない。該当ファイル名と、重みに関する行だけ）
set -e
cd "$(dirname "$0")/.."
REPOS="${X_ALGO_REPOS:-https://github.com/xai-org/x-algorithm}"  # 旧版 twitter/the-algorithm は重いので既定から外した
TMP="${TMPDIR:-/tmp}/x_algo_$$"; mkdir -p "$TMP" data/x_algo
DATE=$(date +%Y%m%d)
OUT="data/x_algo/extract_$DATE.md"
echo "# X 公開アルゴリズム 抜き書き（$DATE）" > "$OUT"
for R in $REPOS; do
  N=$(basename "$R")
  if git clone -q --depth 1 "$R" "$TMP/$N" 2>/dev/null; then
    echo "" >> "$OUT"; echo "## $R" >> "$OUT"
    echo "最終コミット: $(git -C "$TMP/$N" log -1 --format='%cd' --date=short)" >> "$OUT"
    echo "" >> "$OUT"; echo '```' >> "$OUT"
    # 重み・スコアに関する行（名前と数値）だけ。上限 200 行。
    grep -rniE "weight|_score|boost|decay|half_life|penalt" "$TMP/$N" \
      --include='*.scala' --include='*.py' --include='*.rs' --include='*.yml' --include='*.yaml' --include='*.md' --include='*.conf' 2>/dev/null \
      | grep -E "[0-9]" | grep -viE "copyright|license|test" | sed "s#$TMP/$N/##" | head -200 >> "$OUT"
    echo '```' >> "$OUT"
  else
    echo "" >> "$OUT"; echo "## $R" >> "$OUT"; echo "取得できず（リポが無い・非公開・ネットワーク）" >> "$OUT"
  fi
done
rm -rf "$TMP"
echo "$OUT"
echo "次: AI が $OUT を読み、data/x_algo/NOTES.md（人が読める要点・前回との差分）を更新する"
