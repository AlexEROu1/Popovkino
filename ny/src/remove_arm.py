#!/usr/bin/env python3
"""Делает профиль без ближней руки (рука «в кармане») — для анимации броска, где рука рисуется отдельно.
lera_side.png -> lera_side_noarm.png; Настя — ниже, своя разметка (кожанка, свитер, джинсы)."""
import pathlib, numpy as np
from PIL import Image, ImageDraw
here = pathlib.Path(__file__).resolve().parent / 'art'
SLEEVE = [(60,263),(139,263),(138,300),(138,345),(137,390),(126,401),(86,399),(74,386),(66,345),(60,300)]
HAND = [(88,391),(146,391),(147,414),(132,442),(110,452),(90,442)]
def med(a, box):
    x0,y0,x1,y1 = box; p = a[y0:y1, x0:x1].reshape(-1,4); p = p[p[:,3] > 200][:, :3]
    return np.median(p, 0).astype(int)
for name in ['lera_side']:
    im = Image.open(here / f'{name}.png').convert('RGBA'); a = np.array(im).astype(int); H, W = a.shape[:2]
    m = Image.new('L', (W, H), 0); d = ImageDraw.Draw(m); d.polygon(SLEEVE, fill=255); d.polygon(HAND, fill=255)
    mask = np.array(m) > 0
    jacket = med(a, (48, 318, 64, 338)); jeans = med(a, (62, 425, 80, 445))
    dark = (a[..., :3].sum(2) < 200) & (a[..., 3] > 200)
    ink = np.median(a[dark][:, :3], 0).astype(int)
    # низ куртки слева и справа от заплатки
    def hem_at(x):
        col = dark[380:430, x]; ys = np.where(col)[0]; return 380 + int(ys[-1]) if len(ys) else 405
    hl, hr = hem_at(62), hem_at(150)
    out = a.copy()
    for y, x in zip(*np.where(mask)):
        hem = hl + (hr - hl) * (x - 62) / (150 - 62)
        out[y, x, :3] = jacket if y < hem - 1 else jeans
        out[y, x, 3] = 255
    o = Image.fromarray(out.astype('uint8')); d = ImageDraw.Draw(o)
    # линия низа куртки через заплатку
    d.line([(60, hl), (152, hr)], fill=tuple(ink) + (255,), width=3)
    # швы пуховика: соединяем шов слева от заплатки со швом справа
    def seams(x0, x1):
        rows = [y for y in range(268, int(min(hl, hr)) - 8) if dark[y, x0:x1].mean() > .5]
        groups = []
        for y in rows:
            if groups and y - groups[-1][-1] <= 2: groups[-1].append(y)
            else: groups.append([y])
        return [int(np.mean(g)) for g in groups]
    R = sorted(set(seams(140, 152)) | {309, 359}, key=int)
    R = [y for i, y in enumerate(R) if i == 0 or y - R[i-1] > 6]
    # швы на теле идут на тех же высотах, что справа от руки — тянем их через заплатку
    for yr in R:
        d.line([(50, yr - 2), (143, yr)], fill=tuple(ink) + (255,), width=3)
    o.save(here / f'{name}_noarm.png'); print(name, 'jacket', jacket, 'jeans', jeans, 'hem', hl, hr, 'seams', R)

# ---------- Настя: кожанка до y≈350, под ней полоска свитера, ниже джинсы
def nastya():
    im = Image.open(here / 'nastya_side.png').convert('RGBA'); a = np.array(im).astype(int); H, W = a.shape[:2]
    SL = [(66,226),(113,226),(112,262),(108,300),(106,340),(114,370),(112,380),(78,380),(72,366),(67,330)]
    HD = [(82,374),(126,374),(126,396),(114,423),(94,425),(83,406)]
    m = Image.new('L', (W, H), 0); d = ImageDraw.Draw(m); d.polygon(SL, fill=255); d.polygon(HD, fill=255); mask = np.array(m) > 0
    jacket = med(a, (84, 280, 100, 300)); band = (lambda p: np.median(p[(p.sum(1) > 480)], 0).astype(int))(a[364:371, 118:145, :3].reshape(-1, 3)); jeans = med(a, (66, 398, 80, 418))
    dark = (a[..., :3].sum(2) < 170) & (a[..., 3] > 200)
    ink = (28, 22, 20)
    def edges(x):   # границы «кожанка→свитер» и «свитер→джинсы» в столбце x
        col = a[300:400, x, :3]; beige = (col[:, 0] > 150) & (col[:, 1] > 130) & (col[:, 2] > 90)
        ys = np.where(beige)[0]; return (300 + ys[0], 300 + ys[-1]) if len(ys) else (352, 372)
    (t1, b1), (t2, b2) = (354, 366), (362, 373)   # по разметке листа: слева и справа от руки
    out = a.copy()
    for y, x in zip(*np.where(mask)):
        k = (x - 64) / (132 - 64); top = t1 + (t2 - t1) * k; bot = b1 + (b2 - b1) * k
        out[y, x, :3] = jacket if y < top else band if y <= bot else jeans; out[y, x, 3] = 255
    o = Image.fromarray(out.astype('uint8')); d = ImageDraw.Draw(o)
    d.line([(62, t1 - 1), (134, t2 - 1)], fill=ink + (255,), width=3)      # низ кожанки
    d.line([(62, b1 + 1), (134, b2 + 1)], fill=ink + (255,), width=2)      # низ свитера
    for x in range(70, 130, 7):                                            # резинка свитера
        k = (x - 64) / 68; d.line([(x, t1 + (t2 - t1) * k + 2), (x, b1 + (b2 - b1) * k - 1)], fill=(150, 130, 100, 255), width=1)
    o.save(here / 'nastya_side_noarm.png'); print('nastya', 'jacket', jacket, 'band', band, 'jeans', jeans, 'edges', (t1, b1), (t2, b2))
nastya()
