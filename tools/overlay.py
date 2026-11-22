#!/usr/bin/env python3
"""画像に文字を重ねる（サムネ・カルーセル用）。

使い方:
  python3 tools/overlay.py 入力.png 出力.png "1行目" ["2行目"] [--font フォント.ttf] [--size 96] [--pos bottom|center|top]

本人がやること: なし（AI が実行する）。Pillow が無ければ `pip install pillow`。
"""
import argparse, sys
from PIL import Image, ImageDraw, ImageFont

def main():
    p = argparse.ArgumentParser()
    p.add_argument("src"); p.add_argument("dst"); p.add_argument("lines", nargs="+")
    p.add_argument("--font", default=None); p.add_argument("--size", type=int, default=0)
    p.add_argument("--pos", default="bottom", choices=["bottom","center","top"])
    p.add_argument("--color", default="#ffffff"); p.add_argument("--stroke", default="#1a1712")
    a = p.parse_args()
    im = Image.open(a.src).convert("RGBA")
    W, H = im.size
    size = a.size or max(40, W // 12)
    import os
    cands = [a.font] if a.font else []
    cands += [os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fonts", "NotoSansJP-VF.ttf"),
              "/System/Library/Fonts/ヒラギノ角ゴシック W8.ttc", "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"]
    font = None
    for c in cands:
        try:
            font = ImageFont.truetype(c, size)
            try: font.set_variation_by_name("Bold")
            except Exception: pass
            break
        except Exception: continue
    if font is None:
        print("フォントが見つかりません（fonts/NotoSansJP-VF.ttf が無い？）", file=sys.stderr); sys.exit(2)
    # 13字で自動改行
    lines = []
    for l in a.lines:
        while len(l) > 13: lines.append(l[:13]); l = l[13:]
        lines.append(l)
    a.lines = lines
    d = ImageDraw.Draw(im)
    lh = int(size * 1.25); total = lh * len(a.lines)
    y = {"bottom": H - total - H // 12, "center": (H - total) // 2, "top": H // 12}[a.pos]
    for line in a.lines:
        w = d.textlength(line, font=font)
        d.text(((W - w) // 2, y), line, font=font, fill=a.color, stroke_width=max(3, size // 14), stroke_fill=a.stroke)
        y += lh
    im.convert("RGB").save(a.dst, quality=92)
    print(a.dst)

if __name__ == "__main__":
    main()
