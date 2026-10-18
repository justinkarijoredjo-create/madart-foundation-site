import data, urllib.parse as U
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import simpleSplit
from reportlab.pdfbase import pdfmetrics
from PIL import Image
q=lambda s: U.quote(s,safe='')
WA='https://wa.me/'+data.WA_NUM+'?text='
WA_GEN=WA+q(f"Hi {data.CONTACT_FIRST}, I'm interested in the work of {data.MAKER} in Season 03 INLINE, MADART FOUNDATION.")
INK=HexColor('#1E1D1C');CON=HexColor('#C3BDB8');LIN=HexColor('#E1DAD2');CHK=HexColor('#F4EDE4');DAWN=HexColor('#293DCE')
G1=HexColor('#5A5650');G2=HexColor('#8A8680');OKB=HexColor('#DDE8D6');OKT=HexColor('#2F5A3A')
W,H=595.2756,841.8898; M=56; TW=483
c=canvas.Canvas('pdf/raw.pdf',pagesize=(W,H)); c.setTitle(f'{data.MAKER} — Season 03 INLINE — MADART FOUNDATION'); c.setAuthor('MADART FOUNDATION')
def bg(col): c.setFillColor(col); c.rect(0,0,W,H,stroke=0,fill=1)
def T(x,y,s,f='Courier',sz=9,col=INK): c.setFont(f,sz); c.setFillColor(col); c.drawString(x,H-y,s)
def L(x,y,label,url,sz,col=DAWN):
    T(x,y,label,'Courier',sz,col); c.linkURL(url,(x,H-y-2,x+pdfmetrics.stringWidth(label,'Courier',sz),H-y+sz),relative=0)
def link(x,y,label,url,sz):
    T(x,y,label+' ','Courier',sz,DAWN); w=pdfmetrics.stringWidth(label+' ','Courier',sz)
    c.setFont('Symbol',sz); c.drawString(x+w,H-y,'→'); w+=pdfmetrics.stringWidth('→','Symbol',sz)
    c.linkURL(url,(x,H-y-2,x+w,H-y+sz),relative=0)
def para(x,y,s,sz=9,lead=12.5,col=INK,width=TW):
    for ln in simpleSplit(s,'Courier',sz,width): T(x,y,ln,'Courier',sz,col); y+=lead
    return y
SHRUNK=[]
def ribbon(code,band):
    if band: c.setFillColor(LIN); c.rect(0,0,W,H-813.9,stroke=0,fill=1)
    s=f'work by {data.MAKER}   ·   MADART FOUNDATION season 03   ·   100% of the sale proceeds go to the artist   ·   {code}'
    sz=7.5
    while pdfmetrics.stringWidth(s,'Courier',sz)>W-16: sz-=0.1
    if sz<7.5: SHRUNK.append((code,round(sz,2)))
    c.setFont('Courier',sz); c.setFillColor(INK); c.drawCentredString(W/2,H-830.9,s)
# 1 cover
bg(CHK); T(56,70,'MADART FOUNDATION'); T(56,84,'SEASON 03 — INLINE')
for y,ln in zip((410.9,454.9),data.COVER): T(54,y,ln,'Courier-Bold',38)
T(56,490.9,data.GALLERY,'Courier',10)
T(56,771.9,'NIO House Amsterdam · Leidsestraat 32–34','Courier',8.5); T(56,783.9,'Catalogue · 2026','Courier',8.5)
c.showPage()
# 2 collaboration image + maker portraits: full-bleed cover-crop (portrait-page convention)
from PIL import ImageStat
def coverpage(path,label,name):
    iw,ih=Image.open(path).size; s=max(W/iw,H/ih); dw,dh=iw*s,ih*s
    bg(INK); c.drawImage(path,(W-dw)/2,(H-dh)/2,dw,dh)
    im=Image.open(path).convert('L'); x0=int(iw*0.55); y0=int(ih*0.90)
    lum=ImageStat.Stat(im.crop((x0,y0,iw,ih))).mean[0]
    c.setFillColor(INK if lum>140 else CHK)
    if label: c.setFont('Courier',9); c.drawRightString(555.3,H-801.9,label)
    c.setFont('Courier-Bold',13); c.drawRightString(555.3,H-817.9,name)
    CROPS.append((path,iw,ih,round(dw-W),round(dh-H),round(lum)))
    c.showPage()
CROPS=[]
coverpage('pdf/silhouette.jpg','',data.MAKER)
for pp in data.PEOPLE: coverpage(f"pdf/portrait-{pp['key']}.jpg",'Artist',pp['short'].replace(' (I-DO)','') if False else pp['name'].split(' (')[0])
# 3 practice
bg(CHK); T(56,62,'PRACTICE','Courier-Bold',16); y=86
for p in data.IDO+data.SSH+data.WORKS[0]['text']: y=para(56,y,p)+7
y+=11; T(56,y,'POSITION WITHIN INLINE','Courier-Bold',13); y+=20
for p in data.WHY: y=para(56,y,p)+7
y+=11; T(56,y,'IN BRIEF','Courier-Bold',10.5); y+=16
for p in data.IN_BRIEF: y=para(56,y,p,8.5,13,G1)
y+=17.5; T(56,y,'CONTACT','Courier-Bold',10.5); y+=16
for lab,url in data.LINKS: L(56,y,lab,url,8.5); y+=13
T(56,y,f'Sales inquiries are coordinated by {data.CONTACT_FULL} (I-DO).','Courier',8.5,G1); y+=13
L(56,y,f'WhatsApp — message {data.CONTACT_FIRST} directly',WA_GEN,8.5)
print('practice ends at',round(y),'(ribbon band starts 813.9)')
ribbon(f'INLINE-{data.INIT}',True); c.showPage()
# works
BX0,BY0,BX1,BY1=88.9,90.0,506.4,611.9; BW,BH=BX1-BX0,BY1-BY0
for w in data.WORKS:
    p=w['page']; bg(LIN)
    T(56,50,f'{data.GALLERY.upper()} — {data.MAKER.upper()}','Courier',8)
    iw,ih=Image.open(f'pdf/{p}-0.jpg').size; s=min(BW/iw,BH/ih); dw,dh=iw*s,ih*s
    c.drawImage(f'pdf/{p}-0.jpg',BX0+(BW-dw)/2,H-(BY0+(BH-dh)/2)-dh,dw,dh)
    T(56,646.9,w['title'].upper(),'Courier-Bold',13)
    parts=[w['medium'],w['dims'],'Edition of 50']; meta='  ·  '.join(parts)
    lines=[meta] if pdfmetrics.stringWidth(meta,'Courier',8.5)<=TW else [w['medium']+'  ·','  ·  '.join(parts[1:])]
    y=662.9
    for ln in lines: T(56,y,ln,'Courier',8.5,G1); y+=12
    off=(len(lines)-1)*12
    c.setStrokeColor(CON); c.setLineWidth(0.75); c.line(56,H-671.9-off,539.3,H-671.9-off)
    T(56,701.9+off,w['price'],'Courier-Bold',18)
    c.setFillColor(OKB); c.roundRect(474.1,H-697.9-off,65.2,16,8,stroke=0,fill=1)
    c.setFillColor(OKT); c.circle(484.1,H-689.9-off,2.5,stroke=0,fill=1); c.setFont('Courier',8); c.drawString(490.1,H-692.9-off,'available')
    T(56,719.9+off,w['code'],'Courier',8,G2)
    link(56,733.9+off,'inquire via WhatsApp',WA+q(f"Hi {data.CONTACT_FIRST}, I'm interested in '{w['title']}' ({w['code']}) — MADART FOUNDATION, Season 03 INLINE."),8)
    ribbon(w['code'],True); c.showPage()
# acquiring
bg(CHK); T(56,90,'ACQUIRING A WORK','Courier-Bold',18)
y=para(56,126,f"To inquire about a work, tap ‘inquire via WhatsApp’ beneath it, or reference the code shown on the page. Inquiries are sent directly to {data.CONTACT_FULL}, who handles sales on behalf of {data.MAKER} — not to MADART FOUNDATION. 100% of the sale proceeds go to the artist.",10,15)
y+=18; link(56,y,f'Message {data.CONTACT_FIRST} on WhatsApp',WA_GEN,9); y+=16
for lab,url in data.LINKS[:2]: L(56,y,lab,url,9); y+=16
T(56,771.9,'MADART FOUNDATION · Season 03 INLINE · NIO House Amsterdam','Courier',8,G1); T(56,783.9,'Leidsestraat 32–34 · 2026','Courier',8,G1)
c.showPage(); c.save(); print('ribbon shrunk:',SHRUNK); print('crops (overflow w,h pt; lum):',CROPS)
