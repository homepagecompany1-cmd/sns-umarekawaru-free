#!/usr/bin/env python3
"""YouTube に動画をアップロードして公開予約し、サムネを付ける（Data API v3）。

使い方:
  python3 tools/yt_upload.py 動画.mp4 --title "題" --desc 説明.txt --tags "a,b" --thumb サムネ.jpg --at "2026-12-01T19:00:00+09:00" [--shorts]

本人がやること: yt_pull.py と同じ OAuth（スコープに youtube.upload が足りなければ --auth で再許可）。
  実行前に AI は「題・説明・タグ・公開日時・サムネ」を本人に見せて OK をもらう（AGENTS.md 1）。
AI がやること: OK 後に実行。失敗時は 70 のエラー表の前に、クォータ（videos.insert 1日100回・thumbnails.set 約50 units）を疑う。
仕様（確認日 2026-11-22）:
  - status.publishAt で予約。安全側で privacyStatus=private を同時に送る。
  - 未審査アプリの非公開固定は 2026-11-02 の改訂で解除（developers.google.com/youtube/v3/revision_history）。
  - サムネ: JPG/PNG、16:9（Shorts は 9:16）、モバイル 2MB・デスクトップ 50MB（support.google.com/youtube/answer/72431）。
"""
import sys, argparse, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import yt_pull
yt_pull.SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.force-ssl",
                  "https://www.googleapis.com/auth/yt-analytics.readonly"]

def main():
    p = argparse.ArgumentParser(); p.add_argument("video"); p.add_argument("--title", required=True)
    p.add_argument("--desc", help="説明文のファイル"); p.add_argument("--tags", default="")
    p.add_argument("--thumb"); p.add_argument("--at", help="公開日時 ISO8601（例 2026-12-01T19:00:00+09:00）")
    p.add_argument("--shorts", action="store_true"); p.add_argument("--category", default="22")
    a = p.parse_args()
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaFileUpload
    yt = build("youtube", "v3", credentials=yt_pull.creds())
    desc = open(a.desc, encoding="utf-8").read() if a.desc else ""
    if a.shorts and "#Shorts" not in desc: desc += "\n#Shorts"
    body = {"snippet": {"title": a.title[:100], "description": desc[:5000], "tags": [t for t in a.tags.split(",") if t],
                        "categoryId": a.category},
            "status": {"privacyStatus": "private", "selfDeclaredMadeForKids": False}}
    if a.at: body["status"]["publishAt"] = a.at
    req = yt.videos().insert(part="snippet,status", body=body, media_body=MediaFileUpload(a.video, chunksize=8*1024*1024, resumable=True))
    res = None
    while res is None:
        st, res = req.next_chunk()
        if st: print(f"アップロード {int(st.progress()*100)}%")
    vid = res["id"]; print("動画ID:", vid, "公開予定:", a.at or "（予約なし・非公開のまま）")
    if a.thumb:
        yt.thumbnails().set(videoId=vid, media_body=MediaFileUpload(a.thumb)).execute(); print("サムネ設定済み")
    print(f"https://studio.youtube.com/video/{vid}/edit  ← 本人が Studio で最終確認（予約が反映されているか）")

if __name__ == "__main__": main()
