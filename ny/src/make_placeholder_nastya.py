#!/usr/bin/env python3
"""ВРЕМЕННАЯ Настя: перекрашенная Лера (светлые волосы, розовая куртка). Заменить, когда будет её лист."""
import pathlib, numpy as np
from PIL import Image
import colorsys
here = pathlib.Path(__file__).resolve().parent / 'art'
def rgb2hsv(a):
    r,g,b=[a[...,i]/255. for i in range(3)];mx=np.max(a[...,:3],2)/255.;mn=np.min(a[...,:3],2)/255.;d=mx-mn+1e-9
    h=np.where(mx==r,((g-b)/d)%6,np.where(mx==g,(b-r)/d+2,(r-g)/d+4))*60
    s=np.where(mx>0,(mx-mn)/(mx+1e-9),0);return h,s,mx
def hsv2rgb(h,s,v):
    c=v*s;x=c*(1-np.abs((h/60)%2-1));m=v-c;z=np.zeros_like(h)
    conds=[(h<60),(h<120),(h<180),(h<240),(h<300),(h>=300)]
    rs=[c,x,z,z,x,c];gs=[x,c,c,x,z,z];bs=[z,z,x,c,c,x]
    r=np.select(conds,rs);g=np.select(conds,gs);b=np.select(conds,bs)
    return np.stack([(r+m),(g+m),(b+m)],-1)*255
for v in ['front','side','back']:
    im=np.array(Image.open(here/f'lera_{v}.png').convert('RGBA')).astype(float)
    h,s,val=rgb2hsv(im)
    jacket=(h>60)&(h<110)&(s>.45)
    hair=(h>10)&(h<40)&(s>.42)&(val<.80)
    nh=h.copy();ns=s.copy();nv=val.copy()
    nh[jacket]=330;ns[jacket]=s[jacket]*.62;nv[jacket]=np.minimum(1,val[jacket]*1.0)
    nh[hair]=44;ns[hair]=s[hair]*.85;nv[hair]=np.minimum(1,val[hair]*1.45+.08)
    out=im.copy();out[...,:3]=hsv2rgb(nh,ns,nv)
    Image.fromarray(np.clip(out,0,255).astype('uint8')).save(here/f'nastya_{v}.png')
print('ok')
