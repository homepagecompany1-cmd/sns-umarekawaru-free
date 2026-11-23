#!/usr/bin/env python3
"""YouTube の数字を取り込む（Data API v3 + Analytics API）。保存先 data/youtube/ と data/posts/post_log.csv。

本人がやること（1回だけ・platforms/youtube.md の 3）:
  1. Google Cloud でプロジェクト → YouTube Data API v3 / YouTube Analytics API を有効化
  2. OAuth クライアント（デスクトップ）を作り client_secret.json をダウンロード
  3. その場所を .env の YT_CLIENT_SECRET に書く（AI に中身を渡さない）
  4. 初回: python3 tools/yt_pull.py --auth  → ブラウザで許可（本人が押す）

AI がやること: 上の案内のあと `python3 tools/yt_pull.py` を実行し、出力を読んで分析に使う。
必要: pip install google-auth-oauthlib google-api-python-client python-dotenv
クォータ: Data API 1日 10,000 units（channels/playlistItems/videos の list は各 1 unit）。
"""
import os, sys, csv, json, datetime, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
try:
    from dotenv import load_dotenv; load_dotenv(ROOT / ".env")
except Exception: pass
SCOPES = ["https://www.googleapis.com/auth/youtube.readonly",
          "https://www.googleapis.com/auth/yt-analytics.readonly"]
TOKEN = ROOT / ".yt_token.json"

def creds():
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    c = Credentials.from_authorized_user_file(TOKEN, SCOPES) if TOKEN.exists() else None
    if c and c.expired and c.refresh_token: c.refresh(Request())
    if not c or not c.valid or "--auth" in sys.argv:
        secret = os.environ.get("YT_CLIENT_SECRET")
        if not secret or not os.path.exists(secret):
            sys.exit("YT_CLIENT_SECRET（client_secret.json の場所）が .env にありません。本人に platforms/youtube.md の 3 を案内してください")
        c = InstalledAppFlow.from_client_secrets_file(secret, SCOPES).run_local_server(port=0)
        TOKEN.write_text(c.to_json())
    return c

def main():
    from googleapiclient.discovery import build
    c = creds()
    yt = build("youtube", "v3", credentials=c); an = build("youtubeAnalytics", "v2", credentials=c)
    ch = yt.channels().list(part="contentDetails,snippet", mine=True).execute()["items"][0]
    uploads = ch["contentDetails"]["relatedPlaylists"]["uploads"]
    vids, tok = [], None
    while len(vids) < 50:
        r = yt.playlistItems().list(part="contentDetails", playlistId=uploads, maxResults=50, pageToken=tok).execute()
        vids += [i["contentDetails"]["videoId"] for i in r["items"]]; tok = r.get("nextPageToken")
        if not tok: break
    out = []
    for i in range(0, len(vids), 50):
        r = yt.videos().list(part="snippet,statistics", id=",".join(vids[i:i+50])).execute()
        for v in r["items"]:
            out.append({"id": v["id"], "title": v["snippet"]["title"], "published": v["snippet"]["publishedAt"][:10],
                        "views": v["statistics"].get("viewCount"), "likes": v["statistics"].get("likeCount"),
                        "comments": v["statistics"].get("commentCount")})
    end = datetime.date.today(); start = end - datetime.timedelta(days=90)
    a = an.reports().query(ids="channel==MINE", startDate=str(start), endDate=str(end),
                           metrics="views,estimatedMinutesWatched,averageViewDuration,averageViewPercentage,subscribersGained",
                           dimensions="video", sort="-views", maxResults=50).execute()
    am = {row[0]: row[1:] for row in a.get("rows", [])}
    for o in out:
        if o["id"] in am:
            v = am[o["id"]]; o.update({"avg_sec": v[2], "avg_pct": v[3], "subs_gained": v[4]})
    d = ROOT / "data" / "youtube"; d.mkdir(parents=True, exist_ok=True)
    (d / f"videos_{end:%Y%m%d}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    from postlog import upsert
    rows = [{"投稿日": o["published"], "SNS": "YouTube", "種類(画像/カルーセル/動画/文章)": "動画", "最初の1行": o["title"],
             "表示回数": o["views"], "いいね": o["likes"], "コメント": o["comments"],
             "平均視聴時間(秒)": o.get("avg_sec", ""), "平均視聴率(%)": o.get("avg_pct", ""),   # 平均視聴率＝平均で何%見られたか（最後まで見た率とは別）
             "フォロー増": o.get("subs_gained", ""), "投稿ID": f"yt:{o['id']}"} for o in out]
    add, upd = upsert(rows, f"表示回数などは累計・平均視聴と登録者増は {start}〜{end}")
    print(f"{len(out)} 本を保存: {d}  ／ post_log.csv：新しく {add}・数字を更新 {upd}（CTR は Studio の画面で）")

if __name__ == "__main__": main()
