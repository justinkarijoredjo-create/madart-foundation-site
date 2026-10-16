import data, json, re, html, urllib.parse
from PIL import Image
E=html.escape; Q=lambda t: urllib.parse.quote(t,safe='')
WA='https://wa.me/'+data.WA_NUM+'?text='
WA_MAKER=WA+Q("Hello GLINA³, I'm interested in your work in Season 03 INLINE, MADART FOUNDATION.")
SITE='/home/claude/site'; OUT='/home/claude/gl/site'
IGURL='https://www.instagram.com/'+data.IG
src=open(f'{SITE}/eric-sloot.html',encoding='utf-8').read()
head_common=src[src.index('<meta name="twitter:card"'):src.index('<script type="application/ld+json">')]
header=src[src.index('<body>'):src.index('<main id="main">')]
footer_and_scripts=src[src.index('</main>'):]
# rail: from Owen's page (newest), add Owen's own slide (from belle-doxx), sort by name
ow=open(f'{SITE}/owen-mcateer.html',encoding='utf-8').read()
rail=ow[ow.index('<section class="reveal wide">'):ow.index('</main>')]
bd=open(f'{SITE}/belle-doxx.html',encoding='utf-8').read()
i=bd.index('<a class="slide portrait" href="owen-mcateer.html">'); own=bd[i:bd.index('</a>',i)+4]
slides=re.findall(r'(    <a class="slide portrait".*?</a>)',rail,re.S); slides.append('    '+own)
assert not any('glina3.html' in s for s in slides)
slides.sort(key=lambda s:re.search(r'<h3>(.*?)</h3>',s).group(1).lower())
NM=len(slides)+1
rail_new=('<section class="reveal wide"><div class="wrap">\n  <h2 class="index"><span class="no">—</span><span>More makers</span><span class="of">%d in the register</span></h2>\n</div>\n<div class="rail" data-rail data-loop>\n  <div class="track">\n'%NM
  +'\n'.join(slides)+'\n  </div>\n</div>\n<div class="wrap railnav">\n  <button data-prev aria-label="Previous makers">&#8592;</button>\n  <button data-next aria-label="Next makers">&#8594;</button>\n  <span class="hint">Drag, scroll or use the arrows</span>\n  <a class="railall" href="makers.html">All %d makers &#8594;</a>\n</div>\n</section>\n'%NM)
def J(o): return json.dumps(o,ensure_ascii=True)
def head(title,desc,canon,ogimg,ld):
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{canon}">
<meta property="og:site_name" content="MADART FOUNDATION">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:type" content="website">
<meta property="og:image" content="{ogimg}">
<meta property="og:locale" content="en_GB">
{head_common}<script type="application/ld+json">{J(ld)}</script>
</head>
'''
def p_paras(ps): return ''.join(f'<p class="opening">{E(p)}</p>' if i==0 else f'<p>{E(p)}</p>' for i,p in enumerate(ps))
w=data.WORKS[0]; p=w['page']
DESC="An interactive column for body, time and place. 1 work at MADART Foundation, NIO House Amsterdam, 21 October 2026 to 17 January 2027"
tw,th=Image.open(f'{OUT}/t-{p}.jpg').size; pw,ph=Image.open(f'{OUT}/portrait-glina3.jpg').size
card=f'''    <a class="card" href="{p}.html">
      <figure>
<img src="t-{p}.jpg" alt="{E(w['title'])} by GLINA³" width="{tw}" height="{th}" loading="lazy" decoding="async">
      </figure>
      <span class="c">{w['code']}</span>
      <span class="t">{E(w['title'])}</span>
      <div class="m">{E(w['meta'])}</div>
      <div class="p">{w['price']} <span class="pill available">available</span></div>
    </a>'''
ld={"@context":"https://schema.org","@type":"Organization","name":"GLINA³","description":data.LEDE,
    "founder":[{"@type":"Person","name":"Aleksandra Chargeishvili"},{"@type":"Person","name":"Timo Bega"}],
    "location":"Amsterdam","sameAs":[IGURL],"url":data.BASE+"glina3.html"}
maker=head("GLINA³ — MADART FOUNDATION",DESC,data.BASE+"glina3.html",data.BASE+p+".jpg",ld)
maker+=header+f'''<main id="main">

<section class="maker-head"><div class="wrap">
  <p class="index"><span class="no">Season 03 — INLINE</span><span>{data.LOC}</span>
    <span class="of"><a href="makers.html">All makers &#8594;</a></span></p>
  <div class="head-split">
    <div><h1 class="maker-name">GLINA&sup3;</h1></div>
    <div class="head-intro">
      <p class="lede">{E(data.LEDE)}</p>
      <p class="head-links">
<a href="{IGURL}" target="_blank" rel="noopener">Instagram</a><a href="{WA_MAKER}" target="_blank" rel="noopener">Message GLINA&sup3;</a>        <a href="enquire.html">Enquire about a work</a>
      </p>
    </div>
  </div>
</div></section>


<figure class="maker-hero">
  <img src="portrait-glina3.jpg" alt="Aleksandra Chargeishvili and Timo Bega of GLINA³" width="{pw}" height="{ph}" fetchpriority="high" decoding="async">
</figure>

<section class="reveal"><div class="wrap">
  <h2 class="index"><span class="no">01</span><span>Work</span><span class="of">1 recorded</span></h2>
  <div class="grid g2 worklist">
{card}
  </div>
</div></section>

<section class="reveal editorial"><div class="wrap">
  <h2 class="index"><span class="no">02</span><span>Practice</span></h2>
  <div class="ed-body">
{p_paras(data.BIO)}  </div>
</div></section>

<section class="reveal editorial"><div class="wrap">
  <h2 class="index"><span class="no">03</span><span>Why this maker, and where</span></h2>
  <div class="ed-body">
{p_paras(data.WHY)}  </div>
</div></section>




<section class="reveal"><div class="wrap">
  <div class="sales-note">
    <p>100% of the sale proceeds go to the maker. MADART Foundation takes no commission and holds no exclusive contract. Enquiries go directly to GLINA&sup3;.</p>
  </div>
</div></section>

{rail_new}'''+footer_and_scripts
open(f'{OUT}/glina3.html','w',encoding='utf-8').write(maker)
# work page
wsrc=open(f'{SITE}/owen-mcateer-a-box-of-digits-lines.html',encoding='utf-8').read()
STYLE='<style>\n.worklook .desc2{font-size:13px;line-height:1.7;margin:0 0 18px}\n.worklook .extra2{font-size:12px;color:var(--grey);margin:-10px 0 18px}\n</style>\n'
wtail=open(f'{SITE}/eric-sloot-hans-klok.html',encoding='utf-8').read(); wtail=wtail[wtail.index('</main>'):]
wa_work=WA+Q("Hello GLINA³, I'm interested in '"+w['title']+"' ("+w['code']+") — MADART FOUNDATION, Season 03 INLINE.")
wd,ht=Image.open(f'{OUT}/w-{p}.jpg').size
ld={"@context":"https://schema.org","@type":"VisualArtwork","artMedium":w['medium'],"artEdition":w['edition'],"dateCreated":w['year'],
    "creator":{"@type":"Organization","name":"GLINA³","url":data.BASE+"glina3.html"},
    "identifier":w['code'],"image":data.BASE+p+".jpg","name":w['title'],
    "offers":{"@type":"Offer","availability":"https://schema.org/InStock","price":w['price_num'],"priceCurrency":"EUR",
      "priceSpecification":{"@type":"PriceSpecification","price":w['price_num'],"priceCurrency":"EUR","valueAddedTaxIncluded":True},
      "seller":{"@type":"Organization","name":"GLINA³"},"url":w['url']},"url":w['url']}
desc=f"{w['title']} by GLINA³. {w['price']}, and the maker keeps all of it. On view in Season 03 — INLINE at NIO House Amsterdam."
paras=''.join(f'<p class="desc2">{E(t)}</p>' for t in w['text'])
pg=head(f"{w['title']} — GLINA³ — MADART FOUNDATION",desc,w['url'],data.BASE+p+".jpg",ld).replace('</head>',STYLE+'</head>')
pg+=f'''<body class="worklook">
<a class="skip" href="#main">Skip to content</a>

<div class="top2">
  <a href="index.html">MADART FOUNDATION</a>
<span class="live2">SEASON 03 · LIVE</span></div>

<main id="main">
<img class="work" src="w-{p}.jpg" alt="{E(w['title'])}, by GLINA³"
     width="{wd}" height="{ht}"
     fetchpriority="high" decoding="async">
<div class="body2">
  <p class="code2">{w['code']}</p>
  <a class="maker2" href="glina3.html">GLINA&sup3; &#8594;</a>
  <h1>{E(w['title'])}</h1>
  <p class="meta2">{E(w['meta'])}</p>
  <p class="extra2">{E(w['extra'])}</p>
  {paras}

  <div class="priceRow2">
    <span class="price2">{w['price']}</span>
    <span class="pill available">available</span>
  </div>

  <a class="btn" href="enquire.html?work={p}">Enquire about this work</a>
<a class="btn-outline" href="{wa_work}">Or message GLINA&sup3; on WhatsApp</a>  <a class="btn-outline" href="glina3.html">See all work by GLINA&sup3;</a>

  <p class="foot2">
    100% of the sale price goes to the maker. MADART Foundation takes no commission and holds no
    exclusive contract. You buy from GLINA&sup3;; we made the room.
  </p>

  <div class="backline">
<a href="plan-4.html#room-4">Find it on the plan &middot; Gallery 4</a>
    <a href="works.html">All available works</a>
<a href="season-03-inline.html">Season 03 — INLINE</a>    <a href="visit.html">Plan a visit</a>
    <a href="index.html">MADART Foundation</a>
  </div>
</div>
'''+wtail
open(f'{OUT}/{p}.html','w',encoding='utf-8').write(pg)
print('built, register',NM)
