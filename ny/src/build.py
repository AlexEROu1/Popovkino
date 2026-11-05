#!/usr/bin/env python3
"""Собирает ny/game.html из game.src.html: подставляет картинки из art/ в base64.
В шаблоне пишется {{ART:имя_файла}} — заменяется на data:URL. PNG пережимаются в WebP."""
import base64, io, re, pathlib
from PIL import Image
here = pathlib.Path(__file__).resolve().parent
src = (here / 'game.src.html').read_text(encoding='utf-8')
def data_url(name):
    p = here / 'art' / name
    if p.suffix == '.png':
        b = io.BytesIO(); Image.open(p).save(b, 'WEBP', quality=90, method=6); mime = 'image/webp'; raw = b.getvalue()
    else:
        raw = p.read_bytes(); mime = 'image/jpeg'
    return f'data:{mime};base64,' + base64.b64encode(raw).decode()
out = re.sub(r'\{\{ART:([\w.\-]+)\}\}', lambda m: data_url(m.group(1)), src)
dst = here.parent / 'game.html'
dst.write_text(out, encoding='utf-8')
print(dst, round(len(out) / 1024), 'KB')
