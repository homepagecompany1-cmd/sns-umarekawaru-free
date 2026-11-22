#!/usr/bin/env python3
"""X の自分の投稿と数字を取り込む（X API v2・従量課金）。保存先 data/x/ と post_log.csv。

本人がやること（platforms/x.md の 3）: developer.x.com でアプリ → Read 権限の Bearer Token（または OAuth1 の4つ）→ .env の X_BEARER に本人が書く。
料金（確認日 2026-11-22・docs.x.com/x-api/getting-started/pricing）: 投稿の読み取り $0.005/件。
  → AI は実行前に「最大 N 件 × $0.005 = 約 $X」を本人に伝えて OK をもらう。
AI がやること: OK 後 `python3 tools/x_pull.py --username 自分のID --max 50`。
"""
import os, sys, csv, json, datetime, pathlib, argparse, urllib.request, urllib.parse
ROOT = pathlib.Path(__file__).resolve().parent.parent
try:
    from dotenv import load_dotenv; load_dotenv(ROOT / ".env")
except Exception: pass
API = "https://api.x.com/2"

def get(path, **q):
    req = urllib.request.Request(f"{API}/{path}?{urllib.parse.urlencode(q)}", headers={"Authorization": f"Bearer {os.environ['X_BEARER']}"})
    with urllib.request.urlopen(req) as r: return json.load(r)

def main():
    p = argparse.ArgumentParser(); p.add_argument("--max", type=int, default=50); p.add_argument("--username", required=True)
    a = p.parse_args()
    if not os.environ.get("X_BEARER"): sys.exit("X_BEARER が .env にありません。本人に platforms/x.md の 3 を案内してください")
    uid = get(f"users/by/username/{a.username}")["data"]["id"]
    r = get(f"users/{uid}/tweets", max_results=min(100, max(5, a.max)), **{"tweet.fields": "created_at,public_metrics,text"})
    out = r.get("data", [])
    d = ROOT / "data" / "x"; d.mkdir(parents=True, exist_ok=True)
    today = datetime.date.today(); (d / f"tweets_{today:%Y%m%d}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1))
    log = ROOT / "data" / "posts" / "post_log.csv"; seen = set()
    if log.exists():
        with open(log, newline="") as f: seen = {r.get("メモ", "") for r in csv.DictReader(f)}
    with open(log, "a", newline="") as f:
        w = csv.writer(f)
        for t in out:
            key = f"x:{t['id']}"
            if key in seen: continue
            m = t.get("public_metrics", {})
            w.writerow([t["created_at"][:10], "X", "文章", "", t["text"].split("\n")[0][:40], m.get("impression_count"), m.get("like_count"),
                        m.get("reply_count"), m.get("bookmark_count"), m.get("retweet_count", 0) + m.get("quote_count", 0), "", "", "", key])
    print(f"{len(out)} 件を保存: {d} ／ post_log.csv に追記")

if __name__ == "__main__": main()
