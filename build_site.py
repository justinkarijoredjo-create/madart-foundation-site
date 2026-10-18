import data, json, html, urllib.parse
from PIL import Image
SITE='/home/claude/site'; OUT='/home/claude/ido/site'; E=html.escape
Q=lambda t: urllib.parse.quote(t,safe='')
WA='https://wa.me/'+data.WA_NUM+'?text='
WA_MAKER=WA+Q(f"Hi {data.CONTACT_FIRST}, I'm interested in the work of {data.MAKER} in Season 03 INLINE, MADART FOUNDATION.")
MH=E(data.MAKER)
src=open(f'{SITE}/glina3.html',encoding='utf-8').read()
head_common=src[src.index('<meta name="twitter:card"'):src.index('<script type="application/ld+json">')]
header=src[src.index('<body>'):src.index('<main id="main">')]
rail=src[src.index('<section class="reveal wide">'):src.index('</main>')]
footer=src[src.index('</main>'):]
wsrc=open(f'{SITE}/glina3-conditions-of-presence.html',encoding='utf-8').read()
wtail=wsrc[wsrc.index('</main>'):]
WSTYLE=wsrc[wsrc.index('<style>'):wsrc.index('</style>')+8]+'\n'
J=lambda o: json.dumps(o,ensure_ascii=True)
def head(title,desc,canon,ogimg,ld,extra=''):
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
{extra}</head>
'''
def paras(ps): return ''.join(f'<p class="opening">{E(p)}</p>' if i==0 else f'<p>{E(p)}</p>' for i,p in enumerate(ps))
N=len(data.WORKS); P0=data.WORKS[0]['page']
DESC=f"{data.LEDE} {N} work at MADART Foundation, NIO House Amsterdam, 21 October 2026 to 17 January 2027"
cards=[]
for w in data.WORKS:
    tw,th=Image.open(f"{OUT}/t-{w['page']}.jpg").size
    cards.append(f'''    <a class="card" href="{w['page']}.html">
      <figure>
<img src="t-{w['page']}.jpg" alt="{E(w['title'])} by {MH}" width="{tw}" height="{th}" loading="lazy" decoding="async">
      </figure>
      <span class="c">{w['code']}</span>
      <span class="t">{E(w['title'])}</span>
      <div class="m">{E(w['meta'])}</div>
      <div class="p">{w['price']} <span class="pill available">available</span></div>
    </a>''')
ld={"@context":"https://schema.org","@type":"Organization","name":data.MAKER,"description":data.LEDE,
    "member":[{"@type":"Organization","name":"ICONIC DESIGN OBJECTS","url":"https://www.iconicdesignobjects.com"},
              {"@type":"Organization","name":"STUDIOSOPHIEHOSPES","url":"https://www.studiosophiehospes.com"}],
    "sameAs":[u for _,u in data.LINKS],"url":data.BASE+data.SLUG+".html"}
pw,ph=Image.open(f'{OUT}/portrait-{data.SLUG}.jpg').size
headlinks=('<a href="https://www.instagram.com/iconicdesignobjects" target="_blank" rel="noopener">@iconicdesignobjects</a>'
 '<a href="https://www.instagram.com/studiosophiehospes" target="_blank" rel="noopener">@studiosophiehospes</a>'
 '<a href="https://www.iconicdesignobjects.com" target="_blank" rel="noopener">iconicdesignobjects.com</a>'
 '<a href="https://www.studiosophiehospes.com" target="_blank" rel="noopener">studiosophiehospes.com</a>'
 f'<a href="{WA_MAKER}" target="_blank" rel="noopener">Message {data.CONTACT_FIRST} (I-DO)</a>')

blocks=[]
for i,pp in enumerate(data.PEOPLE):
    f=f"portrait-{data.SLUG}-{pp['key']}.jpg"; iw,ih=Image.open(f"{OUT}/{f}").size
    links=' &middot; '.join(f'<a href="{u}" target="_blank" rel="noopener">{E(l)}</a>' for l,u in pp['links'])
    wrap_open='  <div>' if i==0 else '  <div style="margin-top:clamp(52px,7vw,92px);padding-top:clamp(34px,4vw,52px);border-top:var(--hair)">'
    blocks.append(f'''{wrap_open}
    <div style="display:flex;flex-wrap:wrap;gap:clamp(20px,3vw,40px);align-items:flex-start">
      <figure style="flex:0 1 300px;margin:0;background:var(--linen)">
        <img src="{f}" alt="Portrait, {E(pp['short'])}" width="{iw}" height="{ih}"
             style="width:100%;height:auto;aspect-ratio:3/4;object-fit:cover;display:block"
             loading="lazy" decoding="async">
      </figure>
      <div class="ed-body" style="flex:1 1 340px">
        <h3 class="talk-titel">{E(pp['name'])}</h3>
{paras(pp['text'])}<p>{links}</p>      </div>
    </div>
  </div>''')
makers_html='\n'.join(blocks)
maker=head(f"{data.MAKER} — MADART FOUNDATION",DESC,data.BASE+data.SLUG+".html",data.BASE+P0+".jpg",ld)
maker+=header+f'''<main id="main">

<section class="maker-head"><div class="wrap">
  <p class="index"><span class="no">Season 03 — INLINE</span><span>{data.LOC}</span>
    <span class="of"><a href="makers.html">All makers &#8594;</a></span></p>
  <div class="head-split">
    <div><h1 class="maker-name">{MH}</h1></div>
    <div class="head-intro">
      <p class="lede">{E(data.LEDE)}</p>
      <p class="head-links">
{headlinks}        <a href="enquire.html">Enquire about a work</a>
      </p>
    </div>
  </div>
</div></section>


<figure class="maker-hero">
  <img src="portrait-{data.SLUG}.jpg" alt="The silhouette of Ghost behind frosted glass, one hand pressed against it" width="{pw}" height="{ph}" style="object-fit:contain" fetchpriority="high" decoding="async">
</figure>

<section class="reveal"><div class="wrap">
  <h2 class="index"><span class="no">01</span><span>Work</span><span class="of">{N} recorded</span></h2>
  <div class="grid g2 worklist">
{chr(10).join(cards)}
  </div>
</div></section>

<section class="reveal editorial"><div class="wrap">
  <h2 class="index"><span class="no">02</span><span>Practice</span></h2>
  <div class="ed-body">
{paras(data.WORKS[0]['text'])}  </div>
</div></section>

<section class="reveal"><div class="wrap">
  <h2 class="index"><span class="no">03</span><span>Makers</span>
    <span class="of">{len(data.PEOPLE)}</span></h2>
{makers_html}
</div></section>

<section class="reveal editorial"><div class="wrap">
  <h2 class="index"><span class="no">04</span><span>Why this maker, and where</span></h2>
  <div class="ed-body">
{paras(data.WHY)}  </div>
</div></section>




<section class="reveal"><div class="wrap">
  <div class="sales-note">
    <p>100% of the sale proceeds go to the maker. MADART Foundation takes no commission and holds no exclusive contract. Enquiries go directly to {data.CONTACT_FULL} of I-DO.</p>
  </div>
</div></section>

{rail}'''+footer
open(f'{OUT}/{data.SLUG}.html','w',encoding='utf-8').write(maker)

for w in data.WORKS:
    p=w['page']; wd,ht=Image.open(f'{OUT}/w-{p}.jpg').size
    msg="Hi "+data.CONTACT_FIRST+", I'm interested in '"+w['title']+"' ("+w['code']+") — MADART FOUNDATION, Season 03 INLINE."
    wa_work=WA+Q(msg)
    spec={"@type":"PriceSpecification","price":w['price_num'],"priceCurrency":"EUR"}
    if w['vat'] is not None: spec["valueAddedTaxIncluded"]=w['vat']
    ld={"@context":"https://schema.org","@type":"VisualArtwork","artMedium":w['medium'],"artEdition":"Edition of 50",
        "creator":{"@type":"Organization","name":data.MAKER,"url":data.BASE+data.SLUG+".html"},
        "identifier":w['code'],"image":data.BASE+p+".jpg","name":w['title'],
        "height":{"@type":"QuantitativeValue","value":25,"unitCode":"CMT"},
        "width":{"@type":"QuantitativeValue","value":18,"unitCode":"CMT"},
        "depth":{"@type":"QuantitativeValue","value":14,"unitCode":"CMT"},
        "offers":{"@type":"Offer","availability":"https://schema.org/InStock","price":w['price_num'],"priceCurrency":"EUR",
          "priceSpecification":spec,"seller":{"@type":"Organization","name":"ICONIC DESIGN OBJECTS"},"url":w['url']},"url":w['url']}
    desc=f"{w['title']} by {data.MAKER}. {w['price']}, and the maker keeps all of it. On view in Season 03 — INLINE at NIO House Amsterdam."
    body=''.join(f'<p class="desc2">{E(t)}</p>' for t in w['text'])
    pg=head(f"{w['title']} — {data.MAKER} — MADART FOUNDATION",desc,w['url'],data.BASE+p+".jpg",ld,WSTYLE)
    pg+=f'''<body class="worklook">
<a class="skip" href="#main">Skip to content</a>

<div class="top2">
  <a href="index.html">MADART FOUNDATION</a>
<span class="live2">SEASON 03 · LIVE</span></div>

<main id="main">
<img class="work" src="w-{p}.jpg" alt="{E(w['title'])}, by {MH}"
     width="{wd}" height="{ht}"
     fetchpriority="high" decoding="async">
<div class="body2">
  <p class="code2">{w['code']}</p>
  <a class="maker2" href="{data.SLUG}.html">{MH} &#8594;</a>
  <h1>{E(w['title'])}</h1>
  <p class="meta2">{E(w['meta'])}</p>
  <p class="extra2">{E(w['extra'])}</p>
  {body}

  <div class="priceRow2">
    <span class="price2">{w['price']}</span>
    <span class="pill available">available</span>
  </div>

  <a class="btn" href="enquire.html?work={p}">Enquire about this work</a>
<a class="btn-outline" href="{wa_work}">Or message {data.CONTACT_FIRST} on WhatsApp</a>  <a class="btn-outline" href="{data.SLUG}.html">See all work by {MH}</a>

  <p class="foot2">
    100% of the sale price goes to the maker. MADART Foundation takes no commission and holds no
    exclusive contract. You buy from {MH}; we made the room.
  </p>

  <div class="backline">
<a href="plan-4.html#room-5">Find it on the plan &middot; {data.GALLERY}</a>
    <a href="works.html">All available works</a>
<a href="season-03-inline.html">Season 03 — INLINE</a>    <a href="visit.html">Plan a visit</a>
    <a href="index.html">MADART Foundation</a>
  </div>
</div>
'''+wtail
    open(f'{OUT}/{p}.html','w',encoding='utf-8').write(pg)
print('built')
