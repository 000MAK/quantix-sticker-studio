"""Photo -> chat sticker (512x512 WebP, WhatsApp/Telegram ready).

Background removal with rembg (runs locally). Clean cut-outs become die-cut stickers with a white border; subjects
that are cropped by the photo frame (flat cut edges) or mostly lost by the remover become a rounded photo card
instead, so nothing looks broken or overflows. A caption is fitted so it never runs off the sticker.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps
from scipy import ndimage

FONTS = Path(__file__).resolve().parent / "fonts"
_session = None


def font(size: int, weight: int = 800) -> ImageFont.FreeTypeFont:
    f = ImageFont.truetype(str(FONTS / "Exo2-VF.ttf"), size)
    f.set_variation_by_axes([weight])
    return f


def remove_background(img: Image.Image, model: str = "isnet-general-use") -> Image.Image:
    global _session
    from rembg import new_session, remove
    _session = _session or new_session(model)
    return remove(img, session=_session)


def clean(cut: Image.Image) -> Image.Image:
    """Drop specks smaller than 3% of the main piece; full-length shots keep head and upper body."""
    alpha = np.asarray(cut.getchannel("A"))
    labels, n = ndimage.label(alpha > 30)
    if n > 1:
        sizes = ndimage.sum(np.ones_like(labels), labels, range(1, n + 1))
        keep = np.isin(labels, 1 + np.flatnonzero(sizes >= 0.03 * sizes.max()))
        cut.putalpha(Image.fromarray(np.where(keep, alpha, 0).astype("uint8")))
    cut = cut.crop(cut.getbbox())
    if cut.height > 1.8 * cut.width:
        cut = cut.crop((0, 0, cut.width, int(cut.width * 1.25)))
    return cut


def touches_edges(cut: Image.Image) -> bool:
    a = np.asarray(cut.getchannel("A")) > 128
    edges = [a[:3], a[-3:], a[:, :3], a[:, -3:]]
    return sum(e.mean() > 0.12 for e in edges) >= 2


def kept_fraction(cut: Image.Image) -> float:
    return float((np.asarray(cut.getchannel("A")) > 128).mean())


def caption(base: Image.Image, text: str, y: int = 468) -> None:
    d = ImageDraw.Draw(base)
    size = 62
    f = font(size)
    while d.textlength(text, font=f) > 470 and size > 24:
        size -= 2
        f = font(size)
    d.text((256, y), text, font=f, anchor="mm", fill=(58, 40, 36), stroke_width=7, stroke_fill="white")


def die_cut(cut: Image.Image, text: str = "") -> Image.Image:
    cut = clean(cut)
    room = 380 if text else 470
    k = min(470 / cut.width, room / cut.height)
    cut = cut.resize((max(1, int(cut.width * k)), max(1, int(cut.height * k))), Image.LANCZOS)
    base = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    base.alpha_composite(cut, ((512 - cut.width) // 2, 16))
    if text:
        caption(base, text)
    a = base.getchannel("A").point(lambda v: 255 if v > 30 else 0)
    out = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    out.alpha_composite(Image.merge("RGBA", (*[Image.new("L", (512, 512), 255)] * 3, a.filter(ImageFilter.MaxFilter(13)))))
    out.alpha_composite(base)
    return out


def card(img: Image.Image, cut: Image.Image, text: str = "") -> Image.Image:
    box = cut.getchannel("A").point(lambda v: 255 if v > 128 else 0).getbbox() or (0, 0, *img.size)
    cx, cy = (box[0] + box[2]) / 2, box[1] + (box[3] - box[1]) * 0.4
    side = min(img.size)
    left = int(min(max(cx - side / 2, 0), img.width - side))
    top = int(min(max(cy - side / 2, 0), img.height - side))
    size = 400 if text else 470
    photo = img.crop((left, top, left + side, top + side)).resize((size, size), Image.LANCZOS).convert("RGBA")
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, size - 1, size - 1), 44, fill=255)
    out = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    x = (512 - size) // 2
    ImageDraw.Draw(out).rounded_rectangle((x - 9, 6, x + size + 8, 6 + size + 17), 52, fill="white")
    out.paste(photo, (x, 15), mask)
    if text:
        caption(out, text)
    return out


def make_sticker(img: Image.Image, text: str = "", style: str = "auto") -> Image.Image:
    """style: auto | cut | card."""
    img = ImageOps.exif_transpose(img).convert("RGB")
    img.thumbnail((1400, 1400))
    cut = remove_background(img)
    if style == "card" or (style == "auto" and (touches_edges(cut) or kept_fraction(cut) < 0.06)):
        return card(img, cut, text)
    return die_cut(cut, text)


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser(description="Photos -> 512x512 WebP stickers. Caption = text after '_' in the file name.")
    ap.add_argument("src", type=Path, help="folder of photos")
    ap.add_argument("out", type=Path, help="output folder")
    ap.add_argument("--style", default="auto", choices=["auto", "cut", "card"])
    a = ap.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    for p in sorted(a.src.iterdir()):
        if p.suffix.lower() in (".jpg", ".jpeg", ".png", ".webp"):
            text = p.stem.split("_", 1)[1] if "_" in p.stem else ""
            make_sticker(Image.open(p), text, a.style).save(a.out / f"{p.stem}.webp", "WEBP", quality=88, method=6)
            print(p.name)


if __name__ == "__main__":
    main()
