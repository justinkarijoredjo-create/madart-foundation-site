import data, urllib.parse as U
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import simpleSplit
from reportlab.pdfbase import pdfmetrics
from PIL import Image
W_=data.WORKS
WA='https://wa.me/'+data.WA_NUM+'?text='
def q(s): return U.quote(s,safe='')
GEN="Hello GLINA³, I'm interested in your work in Season 03 INLINE, MADART FOUNDATION."
INK=HexColor('#1E1D1C');CON=HexColor('#C3BDB8');LIN=HexColor('#E1DAD2');CHK=HexColor('#F4EDE4');DAWN=HexColor('#293DCE')
G1=HexColor('#5A5650');G2=HexColor('#8A8680');OKB=HexColor('#DDE8D6');OKT=HexColor('#2F5A3A')
W,H=595.2756,841.8898; M=56; TW=W-2*M
P='/home/claude/gl/pdf'
c=canvas.Canvas(f'{P}/raw.pdf',pagesize=(W,H)); c.setTitle('GLINA³ — Season 03 INLINE — MADART FOUNDATION'); c.setAuthor('MADART FOUNDATION')
def bg(col): c.setFillColor(col); c.rect(0,0,W,H,stroke=0,fill=1)
def T(x,y,s,f='Courier',sz=9,col=INK): c.setFont(f,sz); c.setFillColor(col); c.drawString(x,H-y,s)
def link(x,y,label,url,sz):
    T(x,y,label+' ','Courier',sz,DAWN); w=pdfmetrics.stringWidth(label+' ','Courier',sz)
    c.setFont('Symbol',sz); c.drawString(x+w,H-y,'→'); w+=pdfmetrics.stringWidth('→','Symbol',sz)
    c.linkURL(url,(x,H-y-2,x+w,H-y+sz),relative=0)
def tlink(x,y,lab,url,sz):
    T(x,y,lab,'Courier',sz,DAWN); c.linkURL(url,(x,H-y-2,x+pdfmetrics.stringWidth(lab,'Courier',sz),H-y+sz),relative=0)
def para(x,y,s,sz=9,lead=12.5,col=INK,width=TW):
    for ln in simpleSplit(s,'Courier',sz,width): T(x,y,ln,'Courier',sz,col); y+=lead
    return y
def ribbon(code,band):
    if band: c.setFillColor(LIN); c.rect(0,0,W,H-813.9,stroke=0,fill=1)
    s=f'work by GLINA³   ·   MADART FOUNDATION season 03   ·   100% of the sale proceeds go to the artist   ·   {code}'
    sz=7.5
    while pdfmetrics.stringWidth(s,'Courier',sz)>W-16: sz-=0.1
    c.setFont('Courier',sz); c.setFillColor(INK); c.drawCentredString(W/2,H-830.9,s); return sz
# 1 cover — single-line name on the lower name baseline
bg(CHK)
T(56,70,'MADART FOUNDATION'); T(56,84,'SEASON 03 — INLINE')
T(54,454.9,'GLINA³','Courier-Bold',38)
T(56,490.9,'Gallery 4','Courier',10)
T(56,771.9,'NIO House Amsterdam · Leidsestraat 32–34','Courier',8.5); T(56,783.9,'Catalogue · 2026','Courier',8.5)
c.showPage()
# 2 portrait — dark lower right → Chalk Light caption
bg(INK); c.drawImage(f'{P}/portrait.jpg',0,0,W,H)
c.setFillColor(CHK); c.setFont('Courier',9); c.drawRightString(555.3,H-801.9,'Studio')
c.setFont('Courier-Bold',13); c.drawRightString(555.3,H-817.9,'GLINA³')
c.showPage()
# 3 practice
bg(CHK); y=62
T(56,y,'PRACTICE','Courier-Bold',16); y=86
for p in data.BIO: y=para(56,y,p)+7
y+=11; T(56,y,'POSITION WITHIN INLINE','Courier-Bold',13); y+=20
for p in data.WHY: y=para(56,y,p)+7
y+=11; T(56,y,'IN BRIEF','Courier-Bold',10.5); y+=16
y=para(56,y,'Founded by — Aleksandra Chargeishvili and Timo Bega · Amsterdam.',8.5,13,G1)
y=para(56,y,'Previously shown — '+data.EXHIB+'.',8.5,13,G1)
y+=17.5; T(56,y,'CONTACT','Courier-Bold',10.5); y+=16
tlink(56,y,'Instagram — @'+data.IG,'https://www.instagram.com/'+data.IG,8.5); y+=13
tlink(56,y,'WhatsApp — message GLINA³ directly',WA+q(GEN),8.5)
print('practice ends',round(y,1)); ribbon('INLINE-GL3',True); c.showPage()
# works
BX0,BY0,BX1,BY1=88.9,90.0,506.4,611.9; BW,BH=BX1-BX0,BY1-BY0
for w in W_:
    p=w['page']; bg(LIN)
    T(56,50,'GALLERY 4 — GLINA³','Courier',8)
    f=f'{P}/{p}-0.jpg'; iw,ih=Image.open(f).size; s=min(BW/iw,BH/ih); dw,dh=iw*s,ih*s
    c.drawImage(f,BX0+(BW-dw)/2,H-(BY0+(BH-dh)/2)-dh,dw,dh)
    T(56,646.9,w['title'].upper(),'Courier-Bold',13)
    lines=simpleSplit(w['medium']+'  ·','Courier',8.5,TW)+[w['dims']+'  ·  '+w['year']+'  ·  '+w['edition']]
    y=662.9
    for ln in lines: T(56,y,ln,'Courier',8.5,G1); y+=12
    off=(len(lines)-1)*12
    c.setStrokeColor(CON); c.setLineWidth(0.75); c.line(56,H-671.9-off,539.3,H-671.9-off)
    T(56,701.9+off,w['price'],'Courier-Bold',18)
    c.setFillColor(OKB); c.roundRect(474.1,H-697.9-off,65.2,16,8,stroke=0,fill=1)
    c.setFillColor(OKT); c.circle(484.1,H-689.9-off,2.5,stroke=0,fill=1); c.setFont('Courier',8); c.drawString(490.1,H-692.9-off,'available')
    T(56,719.9+off,w['code'],'Courier',8,G2)
    link(56,733.9+off,'inquire via WhatsApp',WA+q(f"Hello GLINA³, I'm interested in '{w['title']}' ({w['code']}) — MADART FOUNDATION, Season 03 INLINE."),8)
    print(w['code'],'meta lines',len(lines),'ribbon',round(ribbon(w['code'],True),2)); c.showPage()
# acquiring
bg(CHK); T(56,90,'ACQUIRING A WORK','Courier-Bold',18)
y=para(56,126,"To inquire about a work, tap ‘inquire via WhatsApp’ beneath it, or reference the code shown on the page. Inquiries are sent directly to GLINA³ — not to MADART FOUNDATION. 100% of the sale proceeds go to the artist.",10,15)
y+=18; link(56,y,'Message GLINA³ on WhatsApp',WA+q(GEN),9); y+=16
tlink(56,y,'Instagram — @'+data.IG,'https://www.instagram.com/'+data.IG,9)
T(56,771.9,'MADART FOUNDATION · Season 03 INLINE · NIO House Amsterdam','Courier',8,G1); T(56,783.9,'Leidsestraat 32–34 · 2026','Courier',8,G1)
c.showPage(); c.save()
