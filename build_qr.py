import data, qrcode, pymupdf
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.lib.utils import simpleSplit
from pyzbar.pyzbar import decode
from PIL import Image
P='/home/claude/bd/pdf'
INK=HexColor('#1E1D1C');CON=HexColor('#C3BDB8');CHK=HexColor('#F4EDE4');G1=HexColor('#5A5650');G2=HexColor('#8A8680')
W,H=595.276,841.89
for w in data.WORKS:
    q=qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M,box_size=20,border=2); q.add_data(w['url']); q.make(fit=True)
    img=q.make_image(fill_color='#1E1D1C',back_color='#F4EDE4').convert('RGB'); f=f'{P}/qr-{w["code"]}.png'; img.save(f)
    got=decode(Image.open(f))[0].data.decode(); assert got==w['url'],(got,w['url']); print('PNG ok',w['code'],got)
c=canvas.Canvas(f'{P}/qr_raw.pdf',pagesize=(W,H)); c.setTitle('Belle Doxx — QR labels — Season 03 INLINE')
LW,LH=W/2,H/3
pos=[]
for k in range(0,len(data.WORKS),6):
    for i,w in enumerate(data.WORKS[k:k+6]):
        col,row=i%2,i//2; x0=col*LW; y0=H-(row+1)*LH; pos.append((k//6,x0,y0,w))
        c.setFillColor(CHK); c.rect(x0,y0,LW,LH,stroke=0,fill=1)
        pad=26; x=x0+pad; y=y0+LH-pad-6
        def t(s,f='Courier',sz=7,colr=INK):
            c.setFont(f,sz); c.setFillColor(colr); c.drawString(x,y,s)
        t('SEASON 03 — INLINE · GALLERY 4',sz=6,colr=G1); y-=24
        t('BELLE DOXX','Courier-Bold',8); y-=16
        for ln in simpleSplit(w['title'].upper(),'Courier-Bold',11,LW-2*pad): t(ln,'Courier-Bold',11); y-=14
        y-=2
        for ln in simpleSplit(w['meta'],'Courier',6.5,LW-2*pad): t(ln,sz=6.5,colr=G1); y-=9
        t(w['extra'],sz=6.5,colr=G1)
        qs=104; c.drawImage(f'{P}/qr-{w["code"]}.png',x0+pad-6,y0+pad-4,qs,qs)
        tx=x0+pad+qs+8; c.setFont('Courier',6.5); c.setFillColor(INK)
        c.drawString(tx,y0+pad+58,'Scan for price'); c.drawString(tx,y0+pad+49,'and enquiries.')
        c.setFillColor(G2); c.setFont('Courier',6); c.drawString(tx,y0+pad+14,w['code']); c.drawString(tx,y0+pad+5,'MADART FOUNDATION')
    c.setStrokeColor(CON); c.setLineWidth(0.4); c.setDash(2,3)
    c.line(LW,0,LW,H); c.line(0,LH,W,LH); c.line(0,2*LH,W,2*LH)
    c.showPage()
c.save()
import subprocess
subprocess.run(['gs','-q','-o',f'{P}/MADART_INLINE_Belle_Doxx_QR-labels.pdf','-sDEVICE=pdfwrite','-dPDFSETTINGS=/printer','-dPrinted=false',f'{P}/qr_raw.pdf'],check=True)
d=pymupdf.open(f'{P}/MADART_INLINE_Belle_Doxx_QR-labels.pdf'); txt=''.join(p.get_text() for p in d)
assert '€' not in txt; print('no € on labels; pages',len(d))
for pg,x0,y0,w in pos:
    pix=d[pg].get_pixmap(matrix=pymupdf.Matrix(3,3)); im=Image.frombytes('RGB',(pix.width,pix.height),pix.samples)
    box=(int(x0*3),int((H-y0-LH)*3),int((x0+LW)*3),int((H-y0)*3)); r=decode(im.crop(box))
    got=r[0].data.decode() if r else None; assert got==w['url'],(w['code'],got); print('label ok',w['code'])
