import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage
S='/tmp/claude-0/-home-claude/a3e60526-7869-5d67-9666-619053c41d3a/scratchpad/art/'
im=np.array(Image.open('/mnt/user-data/attachments/a3e60526-7869-5d67-9666-619053c41d3a/6f04ccdd-image.jpg').convert('RGB')).astype(int)
H,W,_=im.shape
mn=im.min(2);mx=im.max(2)
whiteish=(mn>215)&(mx-mn<25)
lab,n=ndimage.label(whiteish)
edge=set(lab[0])|set(lab[-1])|set(lab[:,0])|set(lab[:,-1]);edge.discard(0)
bg=np.isin(lab,list(edge))
fg=~bg
fg=ndimage.binary_opening(fg,iterations=1)
# columns
cols=fg.sum(0)>0
segs=[];inn=False
for x,c in enumerate(cols):
    if c and not inn:s=x;inn=True
    if not c and inn:segs.append((s,x));inn=False
if inn:segs.append((s,W))
segs=[s for s in segs if s[1]-s[0]>40]
print(segs)
# soft alpha: blur mask slightly
a=Image.fromarray((fg*255).astype('uint8')).filter(ImageFilter.GaussianBlur(0.7))
rgba=Image.fromarray(im.astype('uint8')).convert('RGBA');rgba.putalpha(a)
names=['front','side_bad','back','side']  # 2-я поза: ноги развёрнуты не туда, берём 4-ю
for nm,(x0,x1) in zip(names,segs):
    sub=fg[:,x0:x1];ys=np.where(sub.any(1))[0]
    c=rgba.crop((x0-2,ys[0]-2,x1+2,ys[-1]+3));c.save(S+nm+'.png');print(nm,c.size)
