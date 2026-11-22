# YouTube — 分析・サムネ・公開予約（公式の条件つき）

確認日 2026-11-22。数字・仕様は変わるので、作業の前に AI が出典ページを開いて今の値を見てから進める。

## 1. 数字の取り方（毎週）
### 道A：YouTube Studio の画面（全員・スマホでもできる）
本人が YouTube Studio アプリ／ブラウザで次を開き、スクショを貼る。AI が読み取って `data/youtube/weekly_YYYYMMDD.md` と `data/posts/post_log.csv` に書く。
1. アナリティクス → コンテンツ：動画ごとの **視聴回数・インプレッションのクリック率(CTR)・平均視聴時間**
2. アナリティクス → 視聴者：**「視聴者が見ているもの」**（自分のチャンネル外で視聴者が見た動画・過去7日）
3. アナリティクス → **「リサーチ」**タブ：過去28日に YouTube 全体と似たチャンネルの視聴者が検索した語
4. **Ask Studio**（Studio 内の AI）に「次に作るべき動画」「タイトル案」「サムネ案」を聞き、答えをスクショで貼る。AI はそれを材料に、Claude/Codex の案と並べて出す。
- 出典：Ask Studio https://support.google.com/youtube/answer/16291691 ／視聴者タブ https://support.google.com/youtubecreatorstudio/answer/9314416
- 注意：「Inspiration」タブは Ask Studio へ置き換わる旨のヘルプあり（https://support.google.com/youtube/answer/15575509）。画面に無ければ Ask Studio を使う。

### 道B：API で自動取り込み（PC か クラウド実行がある人）
- **YouTube Analytics API**：再生数・平均視聴率(`averageViewPercentage`)・視聴維持・流入元(`insightTrafficSourceType`) が取れる。スコープ `yt-analytics.readonly`。
  出典 https://developers.google.com/youtube/analytics/channel_reports
- **サムネ CTR** は Analytics API の指標一覧に無く、**Reporting API** の `video_thumbnail_impressions_ctr`（`channel_reach_basic_a1` 等・2026-01-15 追加）で取る。
  出典 https://developers.google.com/youtube/analytics/revision_history
- 道具：`tools/yt_pull.py`

## 2. 公開予約・サムネ（API）
- **Data API v3 のクォータ**：1日 10,000 units（他の全エンドポイント合計）＋ **`videos.insert` は別枠で 1日100回**。`thumbnails.set` は約 50 units。リセットは太平洋時間 0 時。
  出典 https://developers.google.com/youtube/v3/determine_quota_cost ／ https://developers.google.com/youtube/v3/docs/videos/insert
- **公開予約**：`status.publishAt` に日時を入れる。「private が必要か」は公式ページに明記なし（未確認）。`tools/yt_upload.py` は安全側で `privacyStatus=private` ＋ `publishAt` を送る。
- **未審査アプリ**：2026-11-02 の改訂で、未審査アプリからのアップロードが非公開固定になる制限は**解除**された（`privacyStatus` 省略で public。アカウント設定で private になる場合あり）。
  出典 https://developers.google.com/youtube/v3/revision_history
- **サムネの仕様**：動画 16:9（推奨 3840×2160・最小幅 640）、Shorts 9:16（推奨 2160×3840）。JPG/PNG。容量はモバイル 2MB・デスクトップ 50MB。
  出典 https://support.google.com/youtube/answer/72431
- `thumbnails.set` は JPEG/PNG 50MB 以下、スコープは `youtube`/`youtube.upload`/`youtube.force-ssl` のいずれか。カスタムサムネには、チャンネル側の条件（電話番号確認など）が要る場合がある → 本人が Studio で確認。

## 3. 本人がやること（API を使う時・1回だけ）
1. Google Cloud で新しいプロジェクトを作る（本人の Google アカウント）
2. 「YouTube Data API v3」「YouTube Analytics API」を有効にする（CTR は Studio の画面で見る。Reporting API の道具は入っていない）
3. OAuth 同意画面を作り、自分をテストユーザーに入れる
4. OAuth クライアント ID（デスクトップ）を作り、`client_secret.json` をダウンロード → **AI に渡さず**、`.env` の指す場所か Secrets に置く
5. 初回だけ、ブラウザで認可（`tools/yt_pull.py --auth`）
AI は画面の順番だけ案内する。鍵の中身は見ない。

## 4. 予約まで（道A：API なし）
- AI が `out/` に「タイトル3案・説明文・タグ・サムネ3案・公開日時」を用意。
- 本人が YouTube Studio（スマホ可）でアップロード → 「公開予約」で日時を入れる → 確定。
