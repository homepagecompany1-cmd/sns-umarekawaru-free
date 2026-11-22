#!/usr/bin/env python3
"""Instagram に画像・カルーセル・リールを公開する（Instagram API with Instagram Login）。予約は --at（この道具が待つ）。

使い方:
  画像:       python3 tools/ig_publish.py --image https://.../1.jpg --caption 本文.txt [--at "2026-12-01T19:00:00+09:00"]
  カルーセル: python3 tools/ig_publish.py --image URL1 --image URL2 ... --caption 本文.txt
  リール:     python3 tools/ig_publish.py --reel https://.../v.mp4 --caption 本文.txt [--cover URL]
  ※ 画像・動画は「公開 URL」が必要（API の仕様）。R2/Cloudflare など本人の置き場に先に上げる。

本人がやること: ig_pull.py の鍵に加えて権限 instagram_business_content_publish。
  実行前に AI は「本文・画像・日時」を本人に見せて OK をもらう（AGENTS.md 1）。
仕様（確認日 2026-11-22・developers.facebook.com/docs/instagram-platform/content-publishing）:
  - 24h の上限は 100 件（同ページに 50 の記述もあり）。実値は GET /<IG_ID>/content_publishing_limit で確認 → --limit
  - カルーセル最大 20 枚。API に予約機能は無い（この道具が --at まで待ってから公開する。PC/クラウドを起動したままにする）。
"""
import os, sys, time, json, argparse, datetime, pathlib, urllib.request, urllib.parse
ROOT = pathlib.Path(__file__).resolve().parent.parent
try:
    from dotenv import load_dotenv; load_dotenv(ROOT / ".env")
except Exception: pass
API = "https://graph.instagram.com/v24.0"

def call(path, method="GET", **q):
    q["access_token"] = os.environ["IG_TOKEN"]; data = urllib.parse.urlencode(q).encode()
    req = urllib.request.Request(f"{API}/{path}", data=data if method == "POST" else None, method=method)
    url = f"{API}/{path}?{urllib.parse.urlencode(q)}" if method == "GET" else None
    with urllib.request.urlopen(url or req) as r: return json.load(r)

def wait_ready(cid):
    for _ in range(60):
        st = call(cid, fields="status_code").get("status_code")
        if st == "FINISHED": return
        if st in ("ERROR", "EXPIRED"): sys.exit(f"コンテナ {cid} が {st}")
        time.sleep(5)
    sys.exit("処理待ちがタイムアウト")

def main():
    p = argparse.ArgumentParser(); p.add_argument("--image", action="append", default=[]); p.add_argument("--reel")
    p.add_argument("--cover"); p.add_argument("--caption", required=True); p.add_argument("--at"); p.add_argument("--limit", action="store_true"); p.add_argument("--yes", action="store_true", help="これを付けた時だけ公開する")
    a = p.parse_args()
    if not os.environ.get("IG_TOKEN"): sys.exit("IG_TOKEN が .env にありません")
    me = call("me", fields="id,username"); uid = me["id"]
    if a.limit:
        print(json.dumps(call(f"{uid}/content_publishing_limit", fields="quota_usage,config"), ensure_ascii=False)); return
    cap = open(a.caption, encoding="utf-8").read()
    print("=== 下見 ===\n本文:\n" + cap + f"\n画像: {len(a.image)} 枚 / リール: {a.reel or 'なし'} / 日時: {a.at or '今すぐ'}")
    if not a.yes: print("公開していません。本人の OK 後に --yes を付けて実行"); return
    if a.at:
        t = datetime.datetime.fromisoformat(a.at); now = datetime.datetime.now(t.tzinfo)
        if t > now: print(f"{a.at} まで待ちます（{int((t-now).total_seconds()//60)} 分）"); time.sleep((t - now).total_seconds())
    if a.reel:
        c = call(f"{uid}/media", "POST", media_type="REELS", video_url=a.reel, caption=cap, **({"cover_url": a.cover} if a.cover else {}))["id"]
    elif len(a.image) == 1:
        c = call(f"{uid}/media", "POST", image_url=a.image[0], caption=cap)["id"]
    elif 2 <= len(a.image) <= 20:
        kids = []
        for u in a.image:
            k = call(f"{uid}/media", "POST", image_url=u, is_carousel_item="true")["id"]; wait_ready(k); kids.append(k)
        c = call(f"{uid}/media", "POST", media_type="CAROUSEL", children=",".join(kids), caption=cap)["id"]
    else:
        sys.exit("--image（1〜20）か --reel を指定")
    wait_ready(c)
    r = call(f"{uid}/media_publish", "POST", creation_id=c)
    print("公開しました media_id:", r["id"], f"（@{me['username']}）")

if __name__ == "__main__": main()
