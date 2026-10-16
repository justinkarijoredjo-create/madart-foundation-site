import data
from PIL import Image, ImageOps
OUT='/home/claude/bd/site'; PDF='/home/claude/bd/pdf'
def save(im,w,path,q=86):
    im=im.copy()
    if im.width>w: im=im.resize((w,round(im.height*w/im.width)),Image.LANCZOS)
    im.save(path,'JPEG',quality=q,optimize=True,progressive=True,icc_profile=ICC); return im.size
for wk in data.WORKS:
    src=Image.open(wk['src']); ICC=src.info.get('icc_profile'); im=ImageOps.exif_transpose(src).convert('RGB')
    p=wk['page']
    r=[save(im,1600,f'{OUT}/{p}.jpg'),save(im,1600,f'{OUT}/w-{p}.jpg'),save(im,728,f'{OUT}/t-{p}.jpg'),save(im,480,f'{OUT}/h-{p}.jpg'),save(im,1500,f'{PDF}/{p}-0.jpg',88)]
    print(p,im.size,r[1],r[2],r[3])
src=Image.open(data.PORTRAIT_SRC); ICC=src.info.get('icc_profile'); im=ImageOps.exif_transpose(src).convert('RGB')
print('portrait',save(im,1600,f'{OUT}/portrait-belle-doxx.jpg'),save(im,800,f'{OUT}/p-portrait-belle-doxx.jpg'))
# PDF portrait: full-bleed cover-crop to A4 (house convention)
W,H=595.2756,841.8898; r=W/H; iw,ih=im.size
if iw/ih>r: nw=round(ih*r); box=((iw-nw)//2,0,(iw-nw)//2+nw,ih)
else: nh=round(iw/r); box=(0,(ih-nh)//2,iw,(ih-nh)//2+nh)
print('pdf portrait crop box',box,'of',im.size); im.crop(box).save(f'{PDF}/portrait.jpg','JPEG',quality=88,icc_profile=ICC)
