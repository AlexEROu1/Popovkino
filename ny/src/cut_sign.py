import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage
S='/tmp/claude-0/-home-claude/a3e60526-7869-5d67-9666-619053c41d3a/scratchpad/art/'
src=Image.open('/mnt/user-data/attachments/a3e60526-7869-5d67-9666-619053c41d3a/119310fa-image.jpg').convert('RGB')
X0,Y0,X1,Y1=270,360,570,640
im=np.array(src.crop((X0,Y0,X1,Y1))).astype(int)
r,g,b=im[...,0],im[...,1],im[...,2]
brown=(r>g+8)&(g>b+5)&(r>90)
brown=ndimage.binary_opening(brown,iterations=1)
lab,n=ndimage.label(brown);sz=ndimage.sum(brown,lab,range(1,n+1));brown=np.isin(lab,[i+1 for i,s in enumerate(sz) if s>200])
light=im.min(2)>170
lab,n=ndimage.label(light);edge=set(lab[0])|set(lab[-1])|set(lab[:,0])|set(lab[:,-1]);edge.discard(0)
outside=np.isin(lab,list(edge))
near=ndimage.binary_dilation(brown,iterations=13)
m=(~outside)&near
m=ndimage.binary_fill_holes(m|brown)
# post bottom: cut where the post meets snow (lowest brown row)
ys=np.where(brown.any(1))[0];m[ys[-1]+2:]=False
a=Image.fromarray((m*255).astype('uint8')).filter(ImageFilter.GaussianBlur(.6))
o=Image.fromarray(im.astype('uint8')).convert('RGBA');o.putalpha(a)
bb=a.getbbox();o=o.crop(bb);o.save(S+'sign.png');print('sign at',X0+bb[0],Y0+bb[1],o.size)
c=Image.new('RGBA',o.size,(255,40,200,255));c.alpha_composite(o);c.resize((o.size[0]*2,o.size[1]*2)).convert('RGB').save(S+'signcheck.png')
