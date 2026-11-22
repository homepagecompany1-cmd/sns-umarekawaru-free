# Instagram／Threads — インサイト・投稿・予約（公式の条件つき）

確認日 2026-11-22。数字・仕様は変わるので、作業の前に AI が出典ページを開いて今の値を見る。

## 1. 数字の取り方（毎週）
### 道A：公式アプリのインサイト（全員）
プロアカウントの「インサイト」を本人がスクショ → AI が `data/instagram/weekly_YYYYMMDD.md` と `post_log.csv` に書く。見る順：**保存・シェア → リーチ → リール平均視聴時間 → フォロー増**。

### 道B：API（Instagram API with Instagram Login）
- 投稿ごと：`reach` `saved` `shares` `views` `likes` `comments` `follows` `profile_visits`、リールは `ig_reels_avg_watch_time` `reels_skip_rate` も。
  出典 https://developers.facebook.com/docs/instagram-platform/reference/instagram-media/insights
- アカウント：`reach` `accounts_engaged` `follows_and_unfollows` `profile_links_taps` `saves` `shares` `views`。
  出典 https://developers.facebook.com/docs/instagram-platform/api-reference/instagram-user/insights
- `impressions` は廃止済み。道具：`tools/ig_pull.py`

## 2. 投稿（API）
- 必要：**プロアカウント**。権限 `instagram_business_basic` と `instagram_business_content_publish`。
- 審査：Standard Access は審査なし。アプリのロール保有者（管理者・開発者・テスター）は**自分のアカウントに審査なしで使える**。他人のアカウントに使うには Advanced Access（審査）。
  出典 https://developers.facebook.com/docs/graph-api/overview/access-levels
- 上限：24時間で **100件**（同ページ内に 50件の記述もあり矛盾）。実値は `GET /<IG_ID>/content_publishing_limit` で確認する。
- **カルーセル最大 20 枚**（画像・動画の混在可）。リール（`REELS`）・ストーリーズ（`STORIES`）可。音楽付与は公式に記載なし（未確認・公式アプリで付ける）。
- **API に予約投稿は無い**。予約は「アプリ側が時間になったら公開する」形 → `tools/ig_publish.py --at 日時`（PC か クラウドで動かしっぱなしにする必要がある）。スマホだけなら道Aの Meta Business Suite の予約を使う。
  出典 https://developers.facebook.com/docs/instagram-platform/content-publishing

## 3. 予約（道A・全員）
- **Meta Business Suite**（無料）の予約投稿で Instagram/Facebook に予約。何日先まで可かは公式ヘルプで取得できず未確認（実画面で確認）。
  公式ヘルプ https://www.facebook.com/business/help/2223502627919449
- AI は `out/` に本文・ハッシュタグ・画像・日時を用意、本人が Business Suite で予約して確定ボタンを押す。

## 4. Threads
- 投稿 API あり。上限 24時間 **250件**、カルーセル最大 20 枚、予約は API に無し（アプリ側実装）。
- Insights：投稿 `views` `likes` `replies` `reposts` `quotes` `shares`／ユーザー `views` `clicks` `followers_count` `follower_demographics`（権限 `threads_manage_insights`）。
- `threads_content_publish` の Advanced Access が無いと、アプリのテスター以外には投稿できない（自分のアカウントはテスターで可）。
  出典 https://developers.facebook.com/docs/threads/overview ／ /posts ／ /insights

## 5. 本人がやること（API を使う時・1回だけ）
1. Instagram をプロアカウントにする
2. developers.facebook.com でアプリを作り、「Instagram」製品を追加
3. 自分のアカウントをアプリのテスターに入れ、承認する
4. アクセストークンを発行 → **AI に渡さず** Secrets か `.env` に置く（長期トークンに交換する手順も本人が画面で）
AI は画面の順番だけ案内する。
