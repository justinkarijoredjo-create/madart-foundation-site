import data
from PIL import Image
S='site'
def rs(src,w,out,q=86):
    im=Image.open(src).convert('RGB')
    if w and im.width>w: im=im.resize((w,round(im.height*w/im.width)),Image.LANCZOS)
    im.save(out,quality=q,optimize=True,progressive=True); return im.size
print('hero',rs(data.SILHOUETTE,1600,f'{S}/portrait-{data.SLUG}.jpg'))
print('rail',rs(data.SILHOUETTE,800,f'{S}/p-portrait-{data.SLUG}.jpg'))
print('pdf sil',rs(data.SILHOUETTE,1500,'pdf/silhouette.jpg',90))
for p in data.PEOPLE:
    print(p['key'],rs(p['src'],1200,f"{S}/portrait-{data.SLUG}-{p['key']}.jpg"), rs(p['src'],1500,f"pdf/portrait-{p['key']}.jpg",90))
