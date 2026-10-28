"""Hugging Face Space / local web demo: photo -> sticker, meme, animated sticker."""
from __future__ import annotations

import tempfile
from pathlib import Path

import gradio as gr
from PIL import Image

from sticker_studio.animate import frames, save_webp
from sticker_studio.memes import make_meme
from sticker_studio.stickers import make_sticker

SAMPLES = sorted(str(p) for p in (Path(__file__).parent / "samples").glob("*.jpg"))


def sticker_tab(img: Image.Image, text: str, style: str, effect: str):
    if img is None:
        raise gr.Error("Upload a photo first.")
    st = make_sticker(img, text.strip(), style)
    out = Path(tempfile.mkdtemp())
    still = out / "sticker.webp"
    st.save(still, "WEBP", quality=88, method=6)
    anim = save_webp(frames(st, effect), out / "sticker_anim.webp") if effect != "none" else None
    return st, str(still), str(anim) if anim else None


def meme_tab(img: Image.Image, top: str, bottom: str):
    if img is None:
        raise gr.Error("Upload a photo first.")
    return make_meme(img, top, bottom)


with gr.Blocks(title="Quantix Sticker Studio") as demo:
    gr.Markdown("# Quantix Sticker Studio\nPhoto → WhatsApp/Telegram sticker (512×512 WebP), animated sticker, or meme. "
                "Background removal runs on this server with rembg; photos are not stored.")
    with gr.Tab("Sticker"):
        with gr.Row():
            with gr.Column():
                img = gr.Image(type="pil", label="Photo")
                text = gr.Textbox(label="Caption (optional)", placeholder="Seni seviyorum")
                style = gr.Radio(["auto", "cut", "card"], value="auto", label="Style",
                                 info="auto: die-cut when the subject is clean, rounded card when it touches the photo edge")
                effect = gr.Radio(["none", "heartbeat", "shake", "zoom"], value="heartbeat", label="Animation")
                go = gr.Button("Make sticker", variant="primary")
            with gr.Column():
                preview = gr.Image(label="Sticker")
                still = gr.File(label="Static WebP")
                anim = gr.File(label="Animated WebP")
        go.click(sticker_tab, [img, text, style, effect], [preview, still, anim])
        if SAMPLES:
            gr.Examples([[s, "Merhaba!", "auto", "heartbeat"] for s in SAMPLES], [img, text, style, effect])
    with gr.Tab("Meme"):
        with gr.Row():
            with gr.Column():
                mimg = gr.Image(type="pil", label="Photo")
                top = gr.Textbox(label="Top text", value="ME: JUST ONE PHOTO")
                bottom = gr.Textbox(label="Bottom text", value="45 PHOTOS LATER")
                mgo = gr.Button("Make meme", variant="primary")
            mout = gr.Image(label="Meme")
        mgo.click(meme_tab, [mimg, top, bottom], mout)

if __name__ == "__main__":
    demo.launch()
