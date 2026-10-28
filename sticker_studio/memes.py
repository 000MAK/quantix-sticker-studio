"""Classic top/bottom-text meme (Anton font, white with black outline), text auto-shrinks to fit."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

FONTS = Path(__file__).resolve().parent / "fonts"


def make_meme(img: Image.Image, top: str = "", bottom: str = "", size: int = 1080) -> Image.Image:
    im = ImageOps.fit(ImageOps.exif_transpose(img).convert("RGB"), (size, size), Image.LANCZOS, centering=(0.5, 0.4))
    d = ImageDraw.Draw(im)
    for text, y, anchor in ((top, size * 0.04, "ma"), (bottom, size * 0.96, "md")):
        if not text:
            continue
        s = int(size * 0.095)
        f = ImageFont.truetype(str(FONTS / "Anton-Regular.ttf"), s)
        while d.textlength(text.upper(), font=f) > size * 0.93 and s > 30:
            s -= 3
            f = ImageFont.truetype(str(FONTS / "Anton-Regular.ttf"), s)
        d.text((size / 2, y), text.upper(), font=f, anchor=anchor, fill="white", stroke_width=max(3, s // 14), stroke_fill="black")
    return im


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("image", type=Path)
    ap.add_argument("--top", default="")
    ap.add_argument("--bottom", default="")
    ap.add_argument("-o", "--out", type=Path, default=Path("meme.jpg"))
    a = ap.parse_args()
    make_meme(Image.open(a.image), a.top, a.bottom).save(a.out, quality=92)
