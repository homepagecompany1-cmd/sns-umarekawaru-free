#!/usr/bin/env python3
"""post_log.csv の読み書き（x_pull / ig_pull / yt_pull から使う）。
- 同じ投稿（投稿ID）はもう1行足さず、数字だけ最新に書き換える（型・メモなど本人が書いた欄は消さない）。
- ファイルが無ければ見出し行から作る。古い形（投稿IDがメモ欄にある）は自動で直す。
- 取り込むたびに data/posts/metrics_history.csv に「取得日ごとの数字」を残す → 週ごとの増え方が出せる。"""
import csv, datetime, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
LOG = ROOT / "data" / "posts" / "post_log.csv"
HIST = ROOT / "data" / "posts" / "metrics_history.csv"
HEADER = ["投稿日", "SNS", "種類(画像/カルーセル/動画/文章)", "型", "最初の1行", "表示回数", "いいね", "コメント", "保存", "シェア",
          "平均視聴時間(秒)", "最後まで見た率(%)", "平均視聴率(%)", "フォロー増", "数字の取得日", "数字の期間", "投稿ID", "メモ"]
METRICS = ["表示回数", "いいね", "コメント", "保存", "シェア", "平均視聴時間(秒)", "最後まで見た率(%)", "平均視聴率(%)", "フォロー増"]
KEEP = ["種類(画像/カルーセル/動画/文章)", "型", "メモ"]   # 本人が書いた物は上書きしない

def read():
    if not LOG.exists(): return []
    with open(LOG, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    for r in rows:   # 古い形：投稿ID がメモ欄に入っている
        m = (r.get("メモ") or "").strip()
        if not r.get("投稿ID") and m.split(":")[0] in ("x", "ig", "yt") and ":" in m and " " not in m:
            r["投稿ID"], r["メモ"] = m, ""
    return rows

def upsert(new_rows, period=""):
    """new_rows: 見出し名をキーにした dict のリスト（必ず 投稿ID を入れる）。戻り値: (足した数, 直した数)"""
    rows = read(); idx = {r.get("投稿ID"): r for r in rows if r.get("投稿ID")}
    today = datetime.date.today().isoformat(); add = upd = 0
    for n in new_rows:
        n = {k: ("" if v is None else str(v)) for k, v in n.items()}
        n.setdefault("数字の取得日", today); n.setdefault("数字の期間", period)
        cur = idx.get(n["投稿ID"])
        if cur is None:
            rows.append(n); idx[n["投稿ID"]] = n; add += 1
        else:
            for k, v in n.items():
                if k in KEEP and cur.get(k): continue
                if v != "" or k not in METRICS: cur[k] = v
            upd += 1
    LOG.parent.mkdir(parents=True, exist_ok=True)
    tmp = LOG.with_suffix(".tmp")
    with open(tmp, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=HEADER, extrasaction="ignore"); w.writeheader(); w.writerows(rows)
    tmp.replace(LOG)
    first = not HIST.exists()
    with open(HIST, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if first: w.writerow(["取得日", "投稿ID"] + METRICS)
        for n in new_rows: w.writerow([today, n["投稿ID"]] + [("" if n.get(k) is None else n.get(k)) for k in METRICS])
    return add, upd

def weekly_diff(days=7):
    """metrics_history.csv から、各投稿の「days 日前→最新」の増え方を返す（表示回数・いいね・保存・シェア）。"""
    if not HIST.exists(): return []
    with open(HIST, newline="", encoding="utf-8") as f: h = list(csv.DictReader(f))
    by = {}
    for r in h: by.setdefault(r["投稿ID"], []).append(r)
    cut = (datetime.date.today() - datetime.timedelta(days=days)).isoformat(); out = []
    for pid, rs in by.items():
        rs.sort(key=lambda r: r["取得日"]); last = rs[-1]
        base = [r for r in rs if r["取得日"] <= cut]
        if not base: continue
        b = base[-1]
        def d(k):   # どちらかが空（取れなかった回）なら差は出さない（0 として減ったことにしない）
            if not (last.get(k) or "").strip() or not (b.get(k) or "").strip(): return ""
            try: return int(float(last[k])) - int(float(b[k]))
            except ValueError: return ""
        out.append({"投稿ID": pid, "期間": f"{b['取得日']}→{last['取得日']}", **{k: d(k) for k in ("表示回数", "いいね", "保存", "シェア")}})
    return out

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "weekly":
        rs = weekly_diff(int(sys.argv[2]) if len(sys.argv) > 2 else 7)
        if not rs: print("まだ比べられる記録がありません（7日以上あけて2回取り込むと出ます）")
        for r in sorted(rs, key=lambda r: -(r["表示回数"] if isinstance(r["表示回数"], int) else -1)): print(r)
    else:
        print(f"{len(read())} 行（{LOG}）")
