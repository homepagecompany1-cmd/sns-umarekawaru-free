#!/usr/bin/env python3
"""X に投稿する（本文＋画像 最大4枚）。予約は --at（この道具が待つ）。X API v2・従量課金。

使い方: python3 tools/x_post.py --text 本文.txt [--image a.jpg --image b.jpg] [--at "2026-12-01T19:00:00+09:00"]
本人がやること（platforms/x.md の 3）: Read and Write の API Key/Secret・Access Token/Secret を .env に本人が書く
  （X_API_KEY, X_API_SECRET, X_ACCESS_TOKEN, X_ACCESS_SECRET）。
料金（確認日 2026-11-22）: 投稿作成 $0.015/回、URL 付きは $0.200/回。X API に予約機能は無い（Ads API のみ）。
  → AI は実行前に本文・画像・日時・料金を本人に見せて OK をもらう（AGENTS.md 1）。
必要: pip install requests-oauthlib
"""
import os, sys, time, argparse, datetime, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
try:
    from dotenv import load_dotenv; load_dotenv(ROOT / ".env")
except Exception: pass

def main():
    p = argparse.ArgumentParser(); p.add_argument("--text", required=True); p.add_argument("--image", action="append", default=[]); p.add_argument("--at"); p.add_argument("--yes", action="store_true", help="これを付けた時だけ投稿する")
    a = p.parse_args()
    keys = [os.environ.get(k) for k in ("X_API_KEY", "X_API_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_SECRET")]
    if not all(keys): sys.exit("X の鍵4つが .env にありません。本人に platforms/x.md の 3 を案内してください")
    from requests_oauthlib import OAuth1Session
    s = OAuth1Session(*keys)
    text = open(a.text, encoding="utf-8").read().strip()
    if len(a.image) > 4: sys.exit("画像は4枚まで")
    cost = 0.200 if "http" in text else 0.015
    print(f"=== 下見 ===\n{text}\n画像 {len(a.image)} 枚 / 日時 {a.at or '今すぐ'} / 料金の目安 ${cost}（docs.x.com 2026-11-22）")
    if not a.yes: print("投稿していません。本人の OK 後に --yes を付けて実行"); return
    if a.at:
        t = datetime.datetime.fromisoformat(a.at); now = datetime.datetime.now(t.tzinfo)
        if t > now: print(f"{a.at} まで待ちます"); time.sleep((t - now).total_seconds())
    media_ids = []
    for img in a.image:
        with open(img, "rb") as f:
            r = s.post("https://api.x.com/2/media/upload", data={"media_category": "tweet_image"}, files={"media": f})
        r.raise_for_status(); media_ids.append(r.json()["data"]["id"])
    body = {"text": text}
    if media_ids: body["media"] = {"media_ids": media_ids}
    r = s.post("https://api.x.com/2/tweets", json=body); r.raise_for_status()
    print("投稿しました id:", r.json()["data"]["id"])

if __name__ == "__main__": main()
