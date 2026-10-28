"""Static sticker -> animated sticker: WhatsApp animated WebP (<500 KB) and Telegram video sticker (VP9 WEBM, <=3 s,
<256 KB). Effects: heartbeat (double pulse + floating hearts), shake, zoom."""
from __future__ import annotations

import math
import random
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw


def heart(d: ImageDraw.ImageDraw, x: float, y: float, s: float, col: tuple[int, int, int, int]) -> None:
    d.ellipse((x - s, y - s, x, y), fill=col)
    d.ellipse((x, y - s, x + s, y), fill=col)
    d.polygon([(x - s, y - s / 2), (x + s, y - s / 2), (x, y + s)], fill=col)


def frames(sticker: Image.Image, effect: str = "heartbeat", n: int = 30, seed: int = 1) -> list[Image.Image]:
    base = sticker.convert("RGBA").resize((512, 512))
    rng = random.Random(seed)
    bubbles = [(rng.uniform(60, 452), rng.uniform(0, 1), rng.uniform(14, 26)) for _ in range(7)]
    out = []
    for i in range(n):
        t = i / n
        f = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
        if effect == "shake":
            f.alpha_composite(base.rotate(8 * math.sin(2 * math.pi * t * 4), resample=Image.BICUBIC), (int(6 * math.sin(i * 1.9)), 0))
        else:
            s = (1 + 0.045 * max(0.0, math.sin(2 * math.pi * t * 2)) ** 3) * 0.94 if effect == "heartbeat" else 0.82 + 0.16 * (0.5 + 0.5 * math.sin(2 * math.pi * t * 2))
            b = base.resize((int(512 * s),) * 2, Image.LANCZOS)
            f.alpha_composite(b, ((512 - b.width) // 2, (512 - b.height) // 2))
        if effect == "heartbeat":
            layer = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
            d = ImageDraw.Draw(layer)
            for x, phase, s in bubbles:
                p = (t + phase) % 1
                heart(d, x + 12 * math.sin(2 * math.pi * (p + phase)), 500 - p * 470, s, (236, 72, 110, int(230 * (1 - p))))
            f.alpha_composite(layer)
        out.append(f)
    return out


def save_webp(fr: list[Image.Image], path: Path, fps: int = 10) -> Path:
    q = 70
    while True:
        fr[0].save(path, save_all=True, append_images=fr[1:], duration=1000 // fps, loop=0, quality=q, method=4)
        if path.stat().st_size < 480 * 1024 or q <= 20:
            return path
        q -= 12


def save_webm(fr: list[Image.Image], path: Path, fps: int = 10) -> Path:
    import imageio_ffmpeg
    with tempfile.TemporaryDirectory() as tmp:
        for i, f in enumerate(fr):
            f.save(f"{tmp}/{i:03d}.png")
        subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error", "-framerate", str(fps), "-i", f"{tmp}/%03d.png",
                        "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "350k", "-an", "-t", "3", str(path)], check=True)
    return path


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("sticker", type=Path)
    ap.add_argument("--effect", default="heartbeat", choices=["heartbeat", "shake", "zoom"])
    a = ap.parse_args()
    fr = frames(Image.open(a.sticker), a.effect)
    print(save_webp(fr, a.sticker.with_name(a.sticker.stem + "_anim.webp")), save_webm(fr, a.sticker.with_name(a.sticker.stem + "_anim.webm")))
