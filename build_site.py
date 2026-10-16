import data, json, re, html, urllib.parse
from PIL import Image
D=data; E=html.escape
WA='https://wa.me/'+D.WA_NUM+'?text='
Q=lambda t: urllib.parse.quote(t,safe='')
MSG_MAKER="Hi Belle, I'm interested in your work in Season 03 INLINE, MADART FOUNDATION."
WA_MAKER=WA+Q(MSG_MAKER)
SITE='/home/claude/site'; OUT='/home/claude/bd/site'
src=open(f'{SITE}/eric-sloot.html',encoding='utf-8').read()
head_common=src[src.index('<meta name="twitter:card"'):src.index('<script type="application/ld+json">')]
header=src[src.index('<body>'):src.index('<main id="main">')]
footer_and_scripts=src[src.index('</main>'):]
# rail: from the most recent maker page (Owen), plus Owen's own slide, sorted by name
ow=open(f'{SITE}/owen-mcateer.html',encoding='utf-8').read()
rail=ow[ow.index('<section class="reveal wide">'):ow.index('</main>')]
slides=re.findall(r'(    <a class="slide portrait".*?</a>)',rail,re.S)
owen_slide='''    <a class="slide portrait" href="owen-mcateer.html">
      <figure class="swap">
        <img class="face" src="p-portrait-owen-mcateer.jpg" alt="Owen McAteer" width="800" height="559" loading="lazy" decoding="async">
<img class="work" src="h-owen-mcateer-a-box-of-digits-lines.jpg" alt="" width="480" height="270" loading="lazy" decoding="async" aria-hidden="true">      </figure>
      <h3>Owen McAteer</h3>
      <p class="sub">Fourth floor — Gallery 3</p>
      <p class="cnt">4 works</p>
    </a>'''
slides.append(owen_slide)
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
DESC="Seven paintings from the Pixelized Series. 7 works at MADART Foundation, NIO House Amsterdam, 21 October 2026 to 17 January 2027"
cards=[]
for w in D.WORKS:
    tw,th=Image.open(f"{OUT}/t-{w['page']}.jpg").size
    cards.append(f'''    <a class="card" href="{w['page']}.html">
      <figure>
<img src="t-{w['page']}.jpg" alt="{E(w['title'])} by Belle Doxx" width="{tw}" height="{th}" loading="lazy" decoding="async">
      </figure>
      <span class="c">{w['code']}</span>
      <span class="t">{E(w['title'])}</span>
      <div class="m">{E(w['meta'])}</div>
      <div class="p">{w['price']} <span class="pill available">available</span></div>
    </a>''')
ld={"@context":"https://schema.org","@type":"Person","affiliation":{"@type":"NGO","name":"MADART Foundation","url":"https://madartfoundation.com"},
    "description":D.LEDE,"jobTitle":"Artist","name":"Belle Doxx","sameAs":[D.SITE_URL],"url":D.BASE+"belle-doxx.html"}
pw,ph=Image.open(f'{OUT}/portrait-belle-doxx.jpg').size
maker=head("Belle Doxx — MADART FOUNDATION",DESC,D.BASE+"belle-doxx.html",D.BASE+D.WORKS[4]['page']+".jpg",ld)
maker+=header+f'''<main id="main">

<section class="maker-head"><div class="wrap">
  <p class="index"><span class="no">Season 03 — INLINE</span><span>{D.LOC}</span>
    <span class="of"><a href="makers.html">All makers &#8594;</a></span></p>
  <div class="head-split">
    <div><h1 class="maker-name">Belle Doxx</h1></div>
    <div class="head-intro">
      <p class="lede">{E(D.LEDE)}</p>
      <p class="head-links">
<a href="{D.SITE_URL}" target="_blank" rel="noopener">{D.SITE_LABEL}</a><a href="{WA_MAKER}" target="_blank" rel="noopener">Message Belle</a>        <a href="enquire.html">Enquire about a work</a>
      </p>
    </div>
  </div>
</div></section>


<figure class="maker-hero">
  <img src="portrait-belle-doxx.jpg" alt="Belle Doxx in front of a work from the Pixelized Series" width="{pw}" height="{ph}" fetchpriority="high" decoding="async">
</figure>

<section class="reveal"><div class="wrap">
  <h2 class="index"><span class="no">01</span><span>Work</span><span class="of">7 recorded</span></h2>
  <div class="grid g2 worklist">
{chr(10).join(cards)}
  </div>
</div></section>

<section class="reveal editorial"><div class="wrap">
  <h2 class="index"><span class="no">02</span><span>Practice</span></h2>
  <div class="ed-body">
{p_paras(D.BIO)}<p><em>{E(D.STATEMENT_TITLE)}</em></p>{''.join(f'<p>{E(p)}</p>' for p in D.STATEMENT)}  </div>
</div></section>

<section class="reveal editorial"><div class="wrap">
  <h2 class="index"><span class="no">03</span><span>Why this maker, and where</span></h2>
  <div class="ed-body">
{p_paras(D.WHY)}  </div>
</div></section>




<section class="reveal"><div class="wrap">
  <div class="sales-note">
    <p>100% of the sale proceeds go to the maker. MADART Foundation takes no commission and holds no exclusive contract. Enquiries go directly to Belle Doxx.</p>
  </div>
</div></section>

{rail_new}'''+footer_and_scripts
open(f'{OUT}/belle-doxx.html','w',encoding='utf-8').write(maker)
wsrc=open(f'{SITE}/eric-sloot-hans-klok.html',encoding='utf-8').read(); wtail=wsrc[wsrc.index('</main>'):]
for w in D.WORKS:
    msg="Hi Belle, I'm interested in '"+w['title']+"' ("+w['code']+") — MADART FOUNDATION, Season 03 INLINE."
    wa_work=WA+Q(msg)
    p=w['page']; wd,ht=Image.open(f'{OUT}/w-{p}.jpg').size
    ld={"@context":"https://schema.org","@type":"VisualArtwork","artMedium":w['medium'],"artform":"Painting",
        "width":{"@type":"Distance","name":f"{w['w']} cm"},"height":{"@type":"Distance","name":f"{w['h']} cm"},
        "creator":{"@type":"Person","name":"Belle Doxx","url":D.BASE+"belle-doxx.html"},
        "identifier":w['code'],"image":D.BASE+p+".jpg","name":w['title'],
        "offers":{"@type":"Offer","availability":"https://schema.org/InStock","price":w['price_num'],"priceCurrency":"EUR",
          "priceSpecification":{"@type":"PriceSpecification","price":w['price_num'],"priceCurrency":"EUR","valueAddedTaxIncluded":True},
          "seller":{"@type":"Person","name":"Belle Doxx"},"url":w['url']},"url":w['url']}
    desc=f"{w['title']} by Belle Doxx, from the Pixelized Series. {w['price']}, and the maker keeps all of it. On view in Season 03 — INLINE at NIO House Amsterdam."
    pg=head(f"{w['title']} — Belle Doxx — MADART FOUNDATION",desc,w['url'],D.BASE+p+".jpg",ld)
    pg+=f'''<body class="worklook">
<a class="skip" href="#main">Skip to content</a>

<div class="top2">
  <a href="index.html">MADART FOUNDATION</a>
<span class="live2">SEASON 03 · LIVE</span></div>

<main id="main">
<img class="work" src="w-{p}.jpg" alt="{E(w['title'])}, by Belle Doxx"
     width="{wd}" height="{ht}"
     fetchpriority="high" decoding="async">
<div class="body2">
  <p class="code2">{w['code']}</p>
  <a class="maker2" href="belle-doxx.html">Belle Doxx &#8594;</a>
  <h1>{E(w['title'])}</h1>
  <p class="meta2">{E(w['meta'])}</p>

  <div class="priceRow2">
    <span class="price2">{w['price']}</span>
    <span class="pill available">available</span>
  </div>

  <a class="btn" href="enquire.html?work={p}">Enquire about this work</a>
<a class="btn-outline" href="{wa_work}">Or message Belle on WhatsApp</a>  <a class="btn-outline" href="belle-doxx.html">See all work by Belle Doxx</a>

  <p class="foot2">
    100% of the sale price goes to the maker. MADART Foundation takes no commission and holds no
    exclusive contract. You buy from Belle Doxx; we made the room.
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
print('built',NM,'makers in register')
