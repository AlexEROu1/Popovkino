#!/usr/bin/env python3
"""Вырезает персонажа из листа (4 вида в ряд на белом фоне) в отдельные PNG с прозрачностью.
Использование: python3 cut_character.py art/лист.jpg имя front:1 side:2 back:3
  номера — позиции фигур на листе слева направо (1..4); side должен смотреть ВПРАВО.
Пример (Лера): python3 cut_character.py art/lera_sheet.jpg lera front:1 side:4 back:3
  (у Леры 2-я поза с ногами не в ту сторону, поэтому профиль — 4-я)."""
import sys, pathlib
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

here = pathlib.Path(__file__).resolve().parent
sheet, name, *pairs = sys.argv[1:]
want = {k: int(v) for k, v in (p.split(':') for p in pairs)}
im = np.array(Image.open(here / sheet if not pathlib.Path(sheet).is_absolute() else sheet).convert('RGB')).astype(int)
H, W, _ = im.shape
mn, mx = im.min(2), im.max(2)
whiteish = (mn > 215) & (mx - mn < 25)
# белый фон — это светлые области, касающиеся края листа (белые сапоги внутри контура не трогаем)
lab, n = ndimage.label(whiteish)
edge = set(lab[0]) | set(lab[-1]) | set(lab[:, 0]) | set(lab[:, -1]); edge.discard(0)
fg = ~np.isin(lab, list(edge))
fg = ndimage.binary_opening(fg, iterations=1)
# фигуры = группы столбцов с непустыми пикселями
cols = fg.sum(0) > 0
segs, inn = [], False
for x, c in enumerate(cols):
    if c and not inn: s, inn = x, True
    if not c and inn: segs.append((s, x)); inn = False
if inn: segs.append((s, W))
segs = [s for s in segs if s[1] - s[0] > 40]
print('фигуры на листе:', segs)
alpha = Image.fromarray((fg * 255).astype('uint8')).filter(ImageFilter.GaussianBlur(0.7))
rgba = Image.fromarray(im.astype('uint8')).convert('RGBA'); rgba.putalpha(alpha)
for view, idx in want.items():
    x0, x1 = segs[idx - 1]
    sub = fg[:, x0:x1]; ys = np.where(sub.any(1))[0]
    c = rgba.crop((x0 - 2, ys[0] - 2, x1 + 2, ys[-1] + 3))
    out = here / 'art' / f'{name}_{view}.png'; c.save(out); print(out.name, c.size)
