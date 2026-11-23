#!/usr/bin/env python3
"""画像に文字を重ねる（サムネ・カルーセル用）。

使い方:
  python3 tools/overlay.py 入力.png 出力.png "1行目" ["2行目"] [--font フォント.ttf] [--size 96] [--pos bottom|center|top]

本人がやること: なし（AI が実行する）。Pillow が無ければ `pip install pillow`（Linux は `apt-get install -y python3-pil fonts-noto-cjk` でも可）。
文字は画像の幅に合わせて自動で改行・縮小。--max-lines（既定2）行に入らない時は止まるので、言葉を短くする。
"""
import argparse, sys
from PIL import Image, ImageDraw, ImageFont

def main():
    p = argparse.ArgumentParser()
    p.add_argument("src"); p.add_argument("dst"); p.add_argument("lines", nargs="+")
    p.add_argument("--font", default=None); p.add_argument("--size", type=int, default=0)
    p.add_argument("--pos", default="bottom", choices=["bottom","center","top"])
    p.add_argument("--max-lines", type=int, default=2, dest="max_lines"); p.add_argument("--color", default="#ffffff"); p.add_argument("--stroke", default="#1a1712")
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
    # 幅に合わせて改行し、入らなければ文字を小さくする（縁取りも含めて左右の余白の内側に収める）
    d = ImageDraw.Draw(im); margin = W // 14; maxw = W - margin * 2; maxl = a.max_lines
    def load(sz):
        f = ImageFont.truetype(font.path, sz)
        try: f.set_variation_by_name("Bold")
        except Exception: pass
        return f
    def width(t, f, sw): b = d.textbbox((0, 0), t, font=f, stroke_width=sw); return b[2] - b[0]
    def layout(f, sw):
        out = []
        for src in a.lines:
            cur = ""
            for ch in src:
                if cur and width(cur + ch, f, sw) > maxw:
                    out.append(cur); cur = ch
                else: cur += ch
            out.append(cur)
        return out
    size0 = size
    while True:
        sw = max(3, size // 14); f = load(size); lines = layout(f, sw)
        if (len(lines) <= maxl and all(width(l, f, sw) <= maxw for l in lines)) or size <= max(40, int(size0 * 0.6)): break
        size -= 4
    if len(lines) > maxl:
        print(f"⛔ 文字が多すぎて {maxl} 行に入りません（{len(lines)} 行）。言葉を短くしてください：" + " / ".join(a.lines), file=sys.stderr); sys.exit(3)
    font = f
    lh = int(size * 1.25); total = lh * len(lines)
    y = {"bottom": H - total - H // 12, "center": (H - total) // 2, "top": H // 12}[a.pos]
    for line in lines:
        w = width(line, font, sw); bb = d.textbbox((0, 0), line, font=font, stroke_width=sw)
        d.text(((W - w) // 2 - bb[0], y), line, font=font, fill=a.color, stroke_width=sw, stroke_fill=a.stroke)
        y += lh
    if size < size0: print(f"文字が入るように {size0}px → {size}px に小さくしました", file=sys.stderr)
    im.convert("RGB").save(a.dst, quality=92)
    print(a.dst)

if __name__ == "__main__":
    main()
