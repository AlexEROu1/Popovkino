#!/usr/bin/env python3
"""Собирает ny/game.html из game.src.html: подставляет картинки из art/ в base64.
В шаблоне пишется {{ART:имя_файла}} — заменяется на data:URL. PNG пережимаются в WebP.
Кадры заставки: art/intro/k1.jpg … k11.jpg (или .png) — подставляются сами вместо заглушек,
ужимаются до 720 px по ширине. Лера в пижаме: art/lera_pj_side.png (+ front/back) — подключается сама."""
import base64, io, re, pathlib
from PIL import Image
here = pathlib.Path(__file__).resolve().parent
src = (here / 'game.src.html').read_text(encoding='utf-8')

def data_url(name):
    p = here / 'art' / name
    im = Image.open(p)
    if name.startswith('intro/'):
        im = im.convert('RGB')
        if im.width > 720: im = im.resize((720, round(im.height * 720 / im.width)), Image.LANCZOS)
        b = io.BytesIO(); im.save(b, 'JPEG', quality=82, optimize=True); return 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()
    if p.suffix == '.png':
        b = io.BytesIO(); im.save(b, 'WEBP', quality=90, method=6); mime = 'image/webp'; raw = b.getvalue()
    else:
        raw = p.read_bytes(); mime = 'image/jpeg'
    return f'data:{mime};base64,' + base64.b64encode(raw).decode()

# кадры заставки, какие есть
frames = sorted((here / 'art' / 'intro').glob('k*.*')) if (here / 'art' / 'intro').exists() else []
entries = ''.join(f"{f.stem}:img('{{{{ART:intro/{f.name}}}}}')," for f in frames if f.suffix.lower() in ('.jpg', '.jpeg', '.png'))
src = src.replace('/*INTRO_IMAGES*/', entries)
# Лера в пижаме, если лист уже вырезан
if (here / 'art' / 'lera_pj_side.png').exists():
    views = ','.join(f"{v}:img('{{{{ART:lera_pj_{v}.png}}}}')" for v in ('front', 'side', 'back') if (here / 'art' / f'lera_pj_{v}.png').exists())
    src = src.replace('/*LERA_PJ*/', 'lera_pj:{' + views + '},')

out = re.sub(r'\{\{ART:([\w.\-/]+)\}\}', lambda m: data_url(m.group(1)), src)
dst = here.parent / 'game.html'
dst.write_text(out, encoding='utf-8')
print(dst, round(len(out) / 1024), 'KB', '| кадров заставки:', len(frames))
