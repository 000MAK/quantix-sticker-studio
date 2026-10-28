---
title: Quantix Sticker Studio
emoji: 🐱
colorFrom: indigo
colorTo: pink
sdk: gradio
app_file: app.py
license: mit
---

# Quantix Sticker Studio

Turn your own photos into chat stickers, animated stickers and memes, and publish them as a Telegram sticker pack.
Background removal runs locally with [rembg](https://github.com/danielgatis/rembg).

| Module | What it does |
|---|---|
| `sticker_studio/stickers.py` | Photo → 512×512 WebP sticker. Clean cut-outs get a white die-cut border; subjects cropped by the photo frame (or lost by the remover) become a rounded photo card, so nothing overflows. Caption auto-fits. |
| `sticker_studio/animate.py` | Static sticker → animated WebP (WhatsApp, < 500 KB) and VP9 WEBM (Telegram video sticker, ≤ 3 s, < 256 KB): heartbeat, shake, zoom. |
| `sticker_studio/memes.py` | Top/bottom-text meme, auto-shrinking Anton text. |
| `sticker_studio/telegram_pack.py` | Creates or extends a Telegram sticker pack you own, via your own bot (`TELEGRAM_BOT_TOKEN`). |
| `app.py` | Gradio web demo (also the Hugging Face Space). |

## Quick start

```bash
pip install -r requirements.txt
python -m sticker_studio.stickers photos/ stickers_out/          # caption = text after "_" in file name
python -m sticker_studio.animate stickers_out/me_Hello.webp --effect heartbeat
python -m sticker_studio.memes photo.jpg --top "ME: ONE PHOTO" --bottom "45 PHOTOS LATER"
set TELEGRAM_BOT_TOKEN=...   &&   python -m sticker_studio.telegram_pack stickers_out MyPack "My stickers"
python app.py                                                     # web demo on http://127.0.0.1:7860
```

## Privacy

Only use photos of people who agreed. Nothing is uploaded by the CLI tools; the web demo processes the image in
memory and does not store it. Never commit your bot token.

## Credits

- Fonts: Exo 2 (Natanael Gama) and Anton (Vernon Adams), both SIL OFL 1.1 — see `sticker_studio/fonts/`.
- Sample images: Johannes Vermeer, *Girl with a Pearl Earring* (c. 1665) and Théophile-Alexandre Steinlen,
  *Tournée du Chat Noir* (1896) — public domain, via Wikimedia Commons.
- Code: MIT.
