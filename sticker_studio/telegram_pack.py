"""Create (or extend) a Telegram sticker pack owned by you, from a folder of 512 px WebP / WEBM stickers.

One-time: create a bot with @BotFather, press Start in your bot, then
    set TELEGRAM_BOT_TOKEN=123:abc          (never commit the token)
    python -m sticker_studio.telegram_pack stickers_out MyPack "My stickers"
Prints the t.me/addstickers link. Static .webp and video .webm can't share a pack; run once per type.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import requests


def main() -> None:
    folder, short, title = Path(sys.argv[1]), sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else sys.argv[2]
    api = f"https://api.telegram.org/bot{os.environ['TELEGRAM_BOT_TOKEN']}/"
    me = requests.get(api + "getMe", timeout=30).json()["result"]["username"]
    ups = [u["message"]["from"]["id"] for u in requests.get(api + "getUpdates", timeout=30).json()["result"] if "message" in u]
    if not ups:
        sys.exit("Open your bot in Telegram and press Start first.")
    uid, name = ups[-1], f"{short}_by_{me}"
    files = sorted(p for p in folder.iterdir() if p.suffix in (".webp", ".webm"))
    exists = requests.get(api + "getStickerSet", params={"name": name}, timeout=30).json().get("ok")
    for i in range(0, len(files), 50):
        batch = files[i:i + 50]
        up = {f"f{k}": (p.name, p.read_bytes(), "video/webm" if p.suffix == ".webm" else "image/webp") for k, p in enumerate(batch)}
        st = [{"sticker": f"attach://f{k}", "format": "video" if p.suffix == ".webm" else "static", "emoji_list": ["✨"]} for k, p in enumerate(batch)]
        if not exists:
            r = requests.post(api + "createNewStickerSet", files=up, timeout=240, data={"user_id": uid, "name": name, "title": title, "stickers": json.dumps(st)}).json()
            exists = r.get("ok")
        else:
            r = {"ok": all(requests.post(api + "addStickerToSet", timeout=60, files={"f0": up[f"f{k}"]},
                                         data={"user_id": uid, "name": name, "sticker": json.dumps(dict(s, sticker="attach://f0"))}).json().get("ok")
                           for k, s in enumerate(st))}
        print(len(batch), "stickers:", r.get("ok"), r.get("description", ""))
    print(f"https://t.me/addstickers/{name}")


if __name__ == "__main__":
    main()
