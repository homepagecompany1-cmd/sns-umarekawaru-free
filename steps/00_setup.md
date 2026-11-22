# 0-0. 自分のリポを作ってつなぐ（最初の1回だけ・スマホでできる）

このキットは、**あなた専用の非公開リポ**で動かします。公開リポのまま使うと、あなたの事業情報が公開されるので必ずこの手順を先に。

## A：Claude Code の人
1. ブラウザで **https://github.com/homepagecompany1-cmd/sns-umarekawaru-free/generate** を開く（「Use this template」の画面が直接開く。GitHub のログインを求められたら入る）
2. そのまま「Create a new repository」の画面
3. 名前は何でもよい。**Private（非公開）** を選んで作成
4. Claude アプリ → **Code** タブ → 「リポジトリを選ぶ」で、今作ったリポを選ぶ（初回は GitHub の許可画面が出るので許可）
5. 入力欄に「AGENTS.md を読んで、始めて」と送る

## B：Codex の人
1. 上の 1〜3 と同じ（非公開でテンプレートから作る）
2. ChatGPT → **Codex** → 環境（Environment）を作る → GitHub を接続し、今作ったリポを選ぶ
3. 「AGENTS.md を読んで、始めて」と送る。作業は Codex が **PR** を作るので、GitHub アプリで **Merge** を押す（これが保存）

## AI がやること（0-0 の確認）
- `git remote -v` と `gh repo view --json visibility -q .visibility`（gh が無ければ本人に「リポの画面に Private と出ているか」を聞く）で**非公開**を確かめる。公開なら止まって上の手順を案内する。
- 日付・時刻は **Asia/Tokyo** で書く（`TZ=Asia/Tokyo date +%Y%m%d`）。クラウドは UTC なので、そのままだと日付がずれる。
- `state/PROGRESS.md` の 0-0 を `完了` にする。
