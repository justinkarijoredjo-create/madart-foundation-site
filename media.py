import data
from PIL import Image, ImageDraw, ImageFont
S='site'; R=Image.open(data.RENDER).convert('RGB')
p=data.WORKS[0]['page']
def rs(w,out,q=86):
    im=R.resize((w,round(R.height*w/R.width)),Image.LANCZOS); im.save(out,quality=q,optimize=True,progressive=True); return im.size
print('w',rs(1600,f'{S}/w-{p}.jpg')); print('og',rs(1600,f'{S}/{p}.jpg'))
print('t',rs(728,f'{S}/t-{p}.jpg')); print('h',rs(480,f'{S}/h-{p}.jpg'))
print('pdf',rs(1500,f'pdf/{p}-0.jpg',90))
# --- placeholders (explicitly requested by Justin; portraits of both parties to follow)
LIN=(0xE1,0xDA,0xD2); INK=(0x1E,0x1D,0x1C); G=(0x8A,0x86,0x80); CON=(0xC3,0xBD,0xB8)
F=lambda s: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf',s)
def ph(size,panels,out):
    W,H=size; im=Image.new('RGB',size,LIN); d=ImageDraw.Draw(im); n=len(panels)
    for i,(a,b) in enumerate(panels):
        x0=W*i//n; cx=x0+W//(2*n)
        if i: d.line([(x0,0),(x0,H)],fill=CON,width=2)
        fa,fb=F(max(14,W//(42*n))),F(max(12,W//(60*n)))
        for txt,f,col,dy in ((a,fa,INK,-14),(b,fb,G,22)):
            tw=d.textlength(txt,font=f); d.text((cx-tw/2,H/2+dy),txt,font=f,fill=col,anchor='lm' if False else None)
    im.save(out,quality=88); return im.size
PANELS=[("ICONIC DESIGN OBJECTS","portrait to follow"),("STUDIOSOPHIEHOSPES","portrait to follow")]
print('portrait',ph((1600,1118),PANELS,f'{S}/portrait-{data.SLUG}.jpg'))
print('p-portrait',ph((800,1000),[("I-DO \u00d7 SSH","portrait to follow")],f'{S}/p-portrait-{data.SLUG}.jpg'))
print('pdf portraits',ph((900,2546),[PANELS[0]],'pdf/portrait-a.jpg'),ph((900,2546),[PANELS[1]],'pdf/portrait-b.jpg'))
