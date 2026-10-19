#!/usr/bin/env python3
"""白底立绘抠图 v3：floodfill 去背景 + 边缘收缩吃掉白边。"""
import os

from PIL import Image, ImageDraw, ImageFilter

SRC = "/Datas/表情包/fs/形象1.jpeg"
OUT = "/opt/data/cache/scratch/fish-homepage/hero.webp"

img = Image.open(SRC).convert("RGBA")
w, h = img.size
img = img.crop((0, int(h * 0.085), w, h))  # 去掉顶部水印
w, h = img.size

# 四角 floodfill：只删与画布边缘连通的白色
for xy in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)]:
    ImageDraw.floodfill(img, xy, (0, 0, 0, 0), thresh=70)

# 收缩 alpha 边缘 2px，把抗锯齿白边吃掉
alpha = img.getchannel("A")
alpha = alpha.filter(ImageFilter.MinFilter(5))
alpha = alpha.filter(ImageFilter.GaussianBlur(0.6))  # 轻微柔化，避免硬锯齿
img.putalpha(alpha)

bbox = img.getbbox()
if bbox:
    img = img.crop(bbox)

w, h = img.size
target = 560
if w > target:
    img = img.resize((target, int(h * target / w)), Image.LANCZOS)

img.save(OUT, "WEBP", quality=84, method=6)
print("saved:", OUT, img.size, "bytes:", os.path.getsize(OUT))
