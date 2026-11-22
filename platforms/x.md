# X — 公開アルゴリズムの読み込み（週1）・数字・投稿（公式の条件つき）

確認日 2026-11-22。数字・仕様は変わるので、作業の前に AI が出典ページを開いて今の値を見る。

## 1. 公開されている仕組み（オープンソース）を週1で読み直す
X は推薦アルゴリズムを公開している。
- **xai-org/x-algorithm**（2026-01 公開・Apache-2.0・2026-11-21 時点でも更新中）：Transformer（Phoenix）が各行動の確率を予測し、**重み付き和**で並べる。
  - 好意的（プラス）：いいね・リプ・リポスト・引用・共有（DM・リンクコピー）・クリック・滞在/動画視聴時間・投稿者フォロー
  - 否定的（マイナス）：興味なし・ミュート・ブロック・報告・滞在なし
  - 重みの数値は README になく `home-mixer/params/param.rs` にある
  https://github.com/xai-org/x-algorithm
- **twitter/the-algorithm**（2023 公開・AGPL-3.0・最終 push 2025-09）：旧版。
  https://github.com/twitter/the-algorithm

### 毎週の手順
1. `sh tools/x_algo_pull.sh` を実行（重み・スコアに関する行だけを `data/x_algo/extract_YYYYMMDD.md` に抜き出す。生のコードは保存しない）
2. AI が `home-mixer/params/param.rs` などの重みを読み、`data/x_algo/NOTES.md` を更新する：
   - 今の「プラスの行動」「マイナスの行動」と、重みの大小関係（数値は出典行つきで）
   - 前回からの差分
   - **投稿づくりへの反映**（例：リプが来る問い→ リプの重みが大きければ優先。リンクだけの投稿は滞在が短い→ 本文で完結させる 等）
3. `steps/04_kikaku.md` の企画に、NOTES の「反映」を入れる

### 注意
- 公開コードは「本番と同じ」とは限らない。NOTES には「公開版に基づく仮説」と書く。
- 重みを悪用した水増し（相互いいね・bot）はしない。規約違反で凍結の恐れ。

## 2. 数字の取り方
### 道A：画面（全員）
投稿ごとの「アナリティクス」（表示・エンゲージメント・プロフィールクリック）を本人がスクショ → AI が `data/x/` と `post_log.csv` に書く。

### 道B：API
- **料金**：公式 docs.x.com には Free/Basic/Pro の記載がなく**従量課金のみ**（投稿の読み取り $0.005/件、投稿作成 $0.015/回、URL 付き投稿 $0.200/回）。無料で投稿できるかは未確認。
  https://docs.x.com/x-api/getting-started/pricing
- **予約投稿の API は無い**（あるのは広告主向け Ads API だけ）。→ 予約は `tools/x_post.py --at 日時`（アプリ側で待つ）か、X の Web 版の予約機能（公式ヘルプは取得できず未確認・実画面で確認）。
- 画像は 1 投稿 4 枚まで、動画 1 本（`POST /2/media/upload`、`media_category` 必須、動画はチャンク 5MB 以下）。
  https://docs.x.com/x-api/media/upload-media
- **お金がかかる**ので、API を使う前に AI は本人に「1投稿あたりの料金」を伝え、OK をもらう。

## 3. 本人がやること（API を使う時）
1. developer.x.com で開発者アカウントとアプリを作る（支払い方法の登録が要る場合あり）
2. 権限 Read and Write で、API Key/Secret・Access Token/Secret を発行 → **AI に渡さず** Secrets か `.env` へ
AI は画面の順番だけ案内する。
