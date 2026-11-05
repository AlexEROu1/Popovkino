#!/usr/bin/env python3
"""Дорисовывает фон деревни вправо: village.jpg (1280x714) -> village_wide.jpg (2600x714).
Небо, дальние горы, ёлки, снежное поле; на стыке — большая ёлка, закрывающая обрезанную."""
import math, random, pathlib
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

here = pathlib.Path(__file__).resolve().parent
SRC = here / 'art' / 'village.jpg'
DST = here / 'art' / 'village_wide.jpg'
OW, H = 1280, 714
WW = 2600
K = 2  # суперсэмплинг для гладких краёв
random.seed(7)

INK = (29, 29, 29)
SNOW = (218, 227, 234)
SNOW_FAR = (196, 208, 220)
MTN_SNOW = (187, 203, 218)
MTN_GREEN = (48, 80, 82)
TREE_WHITE = (222, 231, 237)
TREE_GREEN = (47, 102, 73)
CLOUD = (124, 145, 188)

def lerp(a, b, t): return tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))

big = Image.new('RGB', (WW * K, H * K))
big.paste(Image.open(SRC).convert('RGB').resize((OW * K, H * K), Image.LANCZOS), (0, 0))
d = ImageDraw.Draw(big)
S = lambda pts: [(x * K, y * K) for x, y in pts]
LW = 3 * K  # толщина контура

# --- небо
for y in range(H):
    t = min(1, y / 260)
    c = lerp((52, 77, 144), (72, 95, 163), t)
    d.line([(OW * K, y * K), (WW * K, y * K)], fill=c, width=K + 1)
# звёзды
for _ in range(26):
    x, y = random.uniform(OW + 20, WW - 10), random.uniform(10, 200)
    r = random.choice([1.6, 2.2, 3])
    d.ellipse([(x - r) * K, (y - r) * K, (x + r) * K, (y + r) * K], fill=(235, 240, 255))
# облака
def cloud(cx, cy, w):
    blobs = [(-0.42, 0.1, .26), (-0.15, -0.12, .3), (0.15, -0.05, .27), (0.4, 0.08, .22), (0, 0.12, .33)]
    for bx, by, br in blobs:
        r = br * w / 2
        d.ellipse([(cx + bx * w / 2 - r * 1.3) * K, (cy + by * w / 3 - r * .7) * K, (cx + bx * w / 2 + r * 1.3) * K, (cy + by * w / 3 + r * .7) * K], fill=CLOUD)
cloud(1620, 72, 300)
cloud(2240, 108, 240)

# --- дальние снежные горы
def ridge(points, fill, base=345):
    pts = [(points[0][0], base)] + points + [(points[-1][0], base)]
    d.polygon(S(pts), fill=fill)
    d.line(S(points), fill=INK, width=LW, joint='curve')
xs = list(range(OW, WW + 80, 20))
far = []
for x in xs:
    y = 236 - 26 * math.sin((x - 1200) / 210) - 14 * math.sin((x - 900) / 77) + 6 * math.sin(x / 31)
    far.append((x, y))
far[0] = (OW, 222)
ridge(far, MTN_SNOW)
near = []
for x in xs:
    y = 262 - 14 * math.sin((x - 1300) / 160) - 8 * math.sin(x / 53)
    near.append((x, y))
near[0] = (OW, 250)
ridge(near, MTN_GREEN)

# --- ёлка в стиле картинки: белая, с зелёными «подтёками», чёрный контур
def tree(cx, base, h, w):
    tiers = 4
    top = base - h
    for i in range(tiers):
        t0 = i / tiers
        ty = top + h * (t0 * 0.78)
        by = top + h * (0.30 + t0 * 0.70) if i < tiers - 1 else base - h * 0.06
        hw = w / 2 * (0.42 + 0.58 * (i + 1) / tiers)
        # треугольник с волнистым низом
        pts = [(cx, ty)]
        n = 8
        pts.append((cx + hw, by))
        for j in range(n + 1):
            x = cx + hw - 2 * hw * j / n
            pts.append((x, by - (5 if j % 2 else 0) * h / 260))
        pts.append((cx - hw, by))
        mask = Image.new('L', big.size, 0)
        ImageDraw.Draw(mask).polygon(S(pts), fill=255)
        layer = Image.new('RGB', big.size, TREE_WHITE)
        ld = ImageDraw.Draw(layer)
        # зелёные пятна-подтёки в нижней части яруса
        gy = by - (by - ty) * 0.24
        for j in range(5):
            gx = cx - hw * 0.8 + 2 * hw * 0.8 * j / 4 + random.uniform(-hw * .06, hw * .06)
            gw = hw * 0.20
            ld.polygon(S([(gx - gw, by + 2), (gx - gw * 0.8, gy + random.uniform(-4, 6)), (gx - gw * 0.2, gy - random.uniform(4, 12) * h / 260),
                          (gx + gw * 0.4, gy + random.uniform(-2, 8)), (gx + gw, by + 2)]), fill=TREE_GREEN)
        big.paste(layer, (0, 0), mask)
        d.line(S(pts + [pts[0]]), fill=INK, width=LW, joint='curve')
    # ствол
    d.rectangle(S([(cx - w * 0.05, base - h * 0.06), (cx + w * 0.05, base + 4)]), fill=(92, 62, 38), outline=INK, width=LW)

# дальний ряд ёлок вдоль горизонта
for x in range(OW + 40, WW + 40, 58):
    hh = random.uniform(62, 92)
    tree(x + random.uniform(-14, 14), 336 + random.uniform(-3, 4), hh, hh * 0.62)

# --- снежное поле
field_top = 332
for y in range(field_top, H):
    t = min(1, (y - field_top) / 90)
    d.line([(OW * K, y * K), (WW * K, y * K + K)], fill=lerp(SNOW_FAR, SNOW, t), width=K + 1)
d.line(S([(OW - 2, field_top), (WW, field_top)]), fill=INK, width=LW)

# столбики старого забора (продолжение)
for x in [1330, 1395, 1458]:
    y = 400 + (x - 1330) * 0.25
    d.rectangle(S([(x - 7, y - 52), (x + 7, y)]), fill=(92, 62, 38), outline=INK, width=LW)
    d.ellipse(S([(x - 9, y - 60), (x + 9, y - 47)]), fill=TREE_WHITE, outline=INK, width=K * 2)

# несколько ёлок по краям поля
tree(1700, 372, 150, 96)
tree(2470, 390, 190, 120)
tree(2560, 420, 230, 140)

# большая ёлка на стыке (закрывает обрезанную ёлку исходной картинки)
tree(1290, 640, 470, 290)

# --- продолжение склона горки: всё, что ниже линии, — снег горки
hill = [(1090, 495), (1150, 527), (1200, 555), (1280, 595), (1330, 625), (1380, 655), (1430, 685), (1470, 714 + 6)]
d.polygon(S(hill + [(1090, 714 + 6)]), fill=SNOW)
d.line(S(hill), fill=INK, width=LW, joint='curve')

# снежные «складки» на поле
for (x0, y0, ln) in [(1560, 520, 90), (1880, 640, 120), (2150, 470, 80), (2330, 600, 110), (2020, 420, 70)]:
    pts = [(x0 + i * ln / 6, y0 + 4 * math.sin(i * 1.2)) for i in range(7)]
    d.line(S(pts), fill=(70, 80, 90), width=K * 2, joint='curve')

out = big.resize((WW, H), Image.LANCZOS)
out.save(DST, quality=88)
print(DST, out.size)
