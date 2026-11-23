# Gemini と Codex の画像生成（公式の条件つき）

確認日 2026-11-22。

## Codex（B の人・画像はこれが一番手軽）
- Codex の画像生成（`gpt-image-2`）は、ChatGPT のプラン利用分に含まれる形で使える場合がある（利用上限の消費は速い）。**使える画面・プラン・上限は変わるので、最初に AI が1枚作って保存できるか試す**。作れなければ、プロンプトを出して本人が ChatGPT／Gemini アプリで作る方法に切り替える。条件は公式で確認：https://learn.chatgpt.com/docs/image-generation
  https://learn.chatgpt.com/docs/image-generation
- 使い方：AI（Codex）に「画像を作って `out/.../thumb_1.png` に保存」と頼む。文字は入れない（`tools/overlay.py` で後から重ねる）。

## Gemini
- 画像モデルの公式名（2026-11 時点）：Nano Banana 2.1 `gemini-nano-banana-2.1`（推奨）／2 `gemini-3.1-flash-image`／Pro `gemini-3-pro-image`／旧 `gemini-2.5-flash-image`（2027-03-15 終了予定）。
- **API の無料枠は無し**（1枚 $0.0336〜$0.134）。
  https://aistudio.google.com/docs/image-generation ／ https://aistudio.google.com/docs/pricing
- Gemini CLI：個人の無料利用は 2026-06-18 に **Antigravity CLI** へ移行（README）。無料枠の回数は未確認。インストール `npm install -g @google/gemini-cli`。スマホ対応は未確認。
  https://github.com/google-gemini/gemini-cli
- 使い方（お金をかけない）：**Gemini アプリ**（スマホ）で画像を作り、`out/` に入れる。タイトル案・サムネ文字案も Gemini アプリに YouTube Studio のスクショを貼って 3 案もらう。
- AI は「Gemini の API を使う」提案をする前に、料金がかかることを本人に伝える。

## 選び方
| 状況 | 使う物 |
|---|---|
| Codex を使っている | Codex の画像生成（追加料金なし） |
| Claude Code だけ・スマホ | ChatGPT アプリ or Gemini アプリで本人が作る（AI は説明文を用意） |
| 大量に作りたい | 料金を本人に伝えて OK をもらってから API |
