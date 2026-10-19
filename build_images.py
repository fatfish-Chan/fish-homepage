#!/usr/bin/env python3
"""压缩素材并导出 base64，供 worker 模板注入。"""
import base64
import os

from PIL import Image

BASE = "/opt/data/cache/scratch/fish-homepage"
SRC_EMOJI = "/Datas/表情包/fs/我是吃白饭的蓝色大肥鱼.webp"


def resize_webp(img, target_w, quality=82):
    w, h = img.size
    if w > target_w:
        img = img.resize((target_w, int(h * target_w / w)), Image.LANCZOS)
    return img


def b64(img):
    tmp = os.path.join(BASE, "_tmp.webp")
    img.save(tmp, "WEBP", quality=82, method=6)
    data = base64.b64encode(open(tmp, "rb").read()).decode()
    os.remove(tmp)
    return data, os.path.getsize(tmp) if os.path.exists(tmp) else 0


# hero：已抠好的透明立绘，压到 620 宽
hero = Image.open(os.path.join(BASE, "hero.webp")).convert("RGBA")
hero = resize_webp(hero, 560)
tmp = os.path.join(BASE, "hero_small.webp")
hero.save(tmp, "WEBP", quality=80, method=6)
hero_b64 = base64.b64encode(open(tmp, "rb").read()).decode()
hero_kb = round(os.path.getsize(tmp) / 1024)

# 白饭表情：白底，压到 460 宽
rice = Image.open(SRC_EMOJI).convert("RGB")
rice = resize_webp(rice, 460)
tmp2 = os.path.join(BASE, "rice_small.webp")
rice.save(tmp2, "WEBP", quality=80, method=6)
rice_b64 = base64.b64encode(open(tmp2, "rb").read()).decode()
rice_kb = round(os.path.getsize(tmp2) / 1024)

open(os.path.join(BASE, "assets.json"), "w").write(
    __import__("json").dumps({"hero": hero_b64, "rice": rice_b64})
)
print(f"hero {hero_kb}KB | rice {rice_kb}KB | b64 total {round((len(hero_b64)+len(rice_b64))/1024)}KB")
