#!/usr/bin/env python3
"""Instagram のインサイトを取り込む（Instagram API with Instagram Login）。保存先 data/instagram/ と post_log.csv。

本人がやること（1回だけ・platforms/instagram.md の 5）:
  1. プロアカウントにする  2. developers.facebook.com でアプリ → Instagram 製品を追加
  3. 自分をテスターに追加して承認  4. アクセストークン（長期）を発行 → .env の IG_TOKEN に本人が書く
  権限: instagram_business_basic（読み取り）/ instagram_business_manage_insights
AI がやること: 案内のあと `python3 tools/ig_pull.py` を実行。
仕様（確認日 2026-11-22）: 投稿ごと reach/saved/shares/views/likes/comments/follows/profile_visits、
  リールは ig_reels_avg_watch_time/reels_skip_rate も（developers.facebook.com/docs/instagram-platform/reference/instagram-media/insights）。
  impressions は廃止。
"""
import os, sys, csv, json, datetime, pathlib, urllib.request, urllib.parse
ROOT = pathlib.Path(__file__).resolve().parent.parent
try:
    from dotenv import load_dotenv; load_dotenv(ROOT / ".env")
except Exception: pass
API = "https://graph.instagram.com/v24.0"

def get(path, **q):
    q["access_token"] = os.environ["IG_TOKEN"]
    with urllib.request.urlopen(f"{API}/{path}?{urllib.parse.urlencode(q)}") as r: return json.load(r)

def main():
    if not os.environ.get("IG_TOKEN"): sys.exit("IG_TOKEN が .env にありません。本人に platforms/instagram.md の 5 を案内してください")
    me = get("me", fields="id,username")
    media = get("me/media", fields="id,caption,media_type,media_product_type,timestamp,permalink", limit=50).get("data", [])
    out = []
    for m in media:
        reel = m.get("media_product_type") == "REELS"
        metrics = "reach,saved,shares,views,likes,comments,follows,profile_visits" + (",ig_reels_avg_watch_time" if reel else "")
        try:
            ins = {d["name"]: d["values"][0]["value"] for d in get(f"{m['id']}/insights", metric=metrics).get("data", [])}
        except Exception as e:
            ins = {"error": str(e)[:80]}
        out.append({**m, "insights": ins})
    d = ROOT / "data" / "instagram"; d.mkdir(parents=True, exist_ok=True)
    today = datetime.date.today()
    (d / f"media_{today:%Y%m%d}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    log = ROOT / "data" / "posts" / "post_log.csv"; seen = set()
    if log.exists():
        with open(log, newline="") as f: seen = {r.get("メモ", "") for r in csv.DictReader(f)}
    with open(log, "a", newline="") as f:
        w = csv.writer(f)
        for o in out:
            key = f"ig:{o['id']}"
            if key in seen: continue
            i = o["insights"]; cap = (o.get("caption") or "").split("\n")[0][:40]
            kind = {"CAROUSEL_ALBUM": "カルーセル", "VIDEO": "動画", "IMAGE": "画像"}.get(o["media_type"], o["media_type"])
            w.writerow([o["timestamp"][:10], "Instagram", kind, "", cap, i.get("views", i.get("reach")), i.get("likes"), i.get("comments"),
                        i.get("saved"), i.get("shares"), i.get("ig_reels_avg_watch_time", ""), "", i.get("follows", ""), key])
    print(f"@{me['username']} {len(out)} 件を保存: {d} ／ post_log.csv に追記")

if __name__ == "__main__": main()
