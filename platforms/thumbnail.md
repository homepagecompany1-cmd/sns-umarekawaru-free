# サムネイル・カルーセル画像の作り方（Codex／Gemini）

## 決まり
- 文字は画像生成に任せず、**あとから重ねる**（AI 画像の文字は崩れる）。生成は「背景＋主役の絵」だけ。
- 顔写真を使う時は本人の物だけ。実在の商品・ロゴ・有名人は入れない。
- 1 枚に文字は 2 行まで・13 字以内／行。スマホで小さく見て読めるか確認する。
- A/B 用に **3 案**作り、本人が選ぶ。選ばれなかった案も `out/` に残す（次週の参考）。

## サイズ（公式の仕様は各 SNS の最新ヘルプで確認。platforms/youtube.md ほかに記載）
- YouTube サムネ：横長（16:9）
- Instagram カルーセル：正方形または縦長（4:5）
- リール／ショート：縦長（9:16）

## 作り方
### B：Codex
1. AI が「画風・主役・背景色・余白・文字なし」の説明文を作る。
2. Codex の画像生成で 3 案作り `out/YYYYMMDD_<番号>/thumb_1.png` 〜 `_3.png` に保存。
3. 文字入れ：`tools/overlay.py`（Pillow）で、`out/.../thumb_text.txt` の文字を重ねる。フォントは本人の端末にある物か、Google Fonts の無料フォントを指定。

### A：Claude Code（画像生成がない場合）
1. AI が同じ説明文を作り `out/.../prompt.txt` に保存。
2. 本人が ChatGPT か Gemini（Nano Banana）に貼って画像を作り、`out/.../` に入れる。
3. 文字入れは同じく `tools/overlay.py`。

### Gemini を使う時
- 画像：**Gemini アプリ（スマホ）**で作る（API は無料枠なし・CLI の無料枠は未確認。platforms/gemini.md）。
- サムネの文字案・タイトル案：Gemini に「視聴者が見ている物（YouTube Studio のスクショ）」を渡して 3 案もらい、Claude/Codex の案と並べて本人が選ぶ。
- 公式の無料枠と制限は platforms/gemini.md。
