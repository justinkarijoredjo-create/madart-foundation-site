MAKER="Belle Doxx"; SLUG="belle-doxx"; FIRST="Belle"
LOC="Fourth floor — Gallery 4 · on the walls"; GALLERY="Gallery 4"
SEASON="Season 03 — INLINE"
BASE="https://madartfoundation.com/"
WA_NUM="31611232849"
SITE_URL="https://www.belledoxx.com"; SITE_LABEL="belledoxx.com"
SERIES_NAME="Pixelized Series"
# order = order of Belle's own artwork PDF (pages 2-8); titles per Justin: Untitled [nr]
RAW=[("Acrylic on canvas",150,120,4500,"img-002"),("Oil on canvas",200,110,6500,"img-003"),
     ("Oil on canvas",120,120,5000,"img-004"),("Oil on canvas",130,90,4500,"img-005"),
     ("Oil on canvas",150,100,5500,"img-006"),("Oil on canvas",50,50,1750,"img-007"),
     ("Acrylic on canvas",80,100,2500,"img-008")]
def eur(n): return "€ "+f"{n:,}".replace(",",".")+",–"
WORKS=[]
for i,(med,w,h,p,src) in enumerate(RAW,1):
    d=dict(n=i,title=f"Untitled {i}",medium=med,w=w,h=h,price_num=p,price=eur(p),src=f"/home/claude/bd/raw/{src}.jpg")
    d["code"]=f"INLINE-BD-{i:02d}"; d["wslug"]=f"untitled-{i}"; d["page"]=f"{SLUG}-untitled-{i}"
    d["url"]=BASE+d["page"]+".html"
    d["dims"]=f"{w} × {h} cm (w × h)"
    d["meta"]=f"{med} · {d['dims']}"
    d["extra"]="Unique · Pixelized Series"
    WORKS.append(d)

BIO=["Belle Doxx is a Dutch contemporary artist whose distinctive visual language brings together painting, symbolism, text, and influences from pop culture and street art.",
"Her work explores the complexities of human nature, moving between identity and ego, freedom and vulnerability, beauty and discomfort, good and evil. Drawing inspiration from cultural anthropology, art history, theology, and the contradictions of contemporary society, Belle is particularly fascinated by the human psyche: its fragility, its tensions, and its capacity for reinvention.",
"Belle completed a Post-Graduate program in Art History and trained in the Bargue drawing technique, studying classical form, structure, chiaroscuro, and the disciplined foundations of academic draftsmanship. This classical training forms an invisible framework beneath a visual language that is raw, instinctive, and emotionally charged.",
"For Belle, beauty is not an end in itself, but a tool: a way to connect, disrupt, seduce, and unsettle. In a culture where identity and image increasingly blur into performance, her work invites the viewer to question what lies beneath the surface.",
"Her work has been presented in solo exhibitions at Shelter Amsterdam and Gallery BLNDSH in The Hague, as well as at the NOCKNOCK Art Fair. She has also participated in group exhibitions in Amsterdam and Antwerp, including Black Art Gallery, where her work was shown alongside artists such as Harif Guzman and Stig De Block. Her work is held in private collections in the Netherlands, Belgium, and beyond.",
"Beyond the traditional gallery space, Belle has collaborated with international artist Machine Gun Kelly, creating custom artwork for merchandise, and with Dutch fashion house In Gold We Trust on a limited-edition artistic sweater. In 2025, her work was also presented by Playboy.",
"Belle Doxx creates art at the intersection of energy, emotion, and intellect. Her paintings are unapologetically human: seductive yet confrontational, instinctive yet considered, inviting the viewer not simply to look, but to question, unravel, and feel."]

STATEMENT_TITLE="Pixelated Bodies"
STATEMENT=["An important inspiration for my paintings is the ancient mosaic art of Pompeii. I am fascinated by the connection between mosaic stones and digital pixels: both are small fragments that come together to form an image. By translating pixels into oil paint, I bring together the classical and the contemporary, connecting ancient imagery with today’s screen-dominated culture.",
"In ancient mosaics, small stones were used to reveal the human body. Today, we see almost everything through screens, yet we still struggle with the idea of seeing the body fully exposed.",
"This contrast is central to my work. In Pompeii, nudity and sensuality were openly depicted in art thousands of years ago. Yet today, despite living in a world where we are constantly surrounded by images of bodies, we still seem uncomfortable with female nudity. Why is something that has existed in art for centuries still considered provocative?",
"I paint my own breasts and body as a grid of oil-painted squares, inspired by the pixels that make up the images we see on our screens every day. My body becomes both visible and hidden, revealing and concealing at the same time. The paintings reflect the way we experience images today, while questioning our changing relationship with female nudity, sensuality and censorship.",
"I am aware that these paintings can be provocative, but that is also part of their purpose. While we often think of ourselves as sexually liberated, I feel that society is becoming increasingly conservative. The openness and freedom surrounding nudity in the 1980s and 1990s seem to be fading. We have access to more images than ever before, yet the female body remains something to censor, judge and control.",
"I also want to challenge the assumption that a woman expressing her sensuality is seeking male attention. To me, sensuality is not necessarily about sex or being desired. It can be an important part of feeling feminine, confident and connected to your own body. Being comfortable with your beauty does not mean wanting to be objectified.",
"Religion and cultural traditions continue to shape how women and their bodies are perceived. Despite the progress we have made, female freedom and self-expression remain complicated issues. In many societies, religious and cultural expectations still place restrictions on how women are allowed to dress, behave and express their sensuality. The female body remains caught between admiration, desire, shame and control.",
"We live in a time when almost everything is visible, when images of bodies fill our screens every day. Yet somehow, we have still not become comfortable with nudity itself.",
"Thousands of years after the mosaics of Pompeii, why does the naked female body still make us uncomfortable?",
"Ultimately, my paintings question not only what we see, but why we react to it."]

LEDE="Seven canvases from the Pixelized Series. Belle Doxx paints her own body square by square, in oil and acrylic, at the coarse resolution a screen uses for what it will not show."

WHY=["INLINE looks at the point where the screen and the room stop being separate places. The Pixelized Series sits on that line. Its grid is borrowed from the screen, from the blocky pixelation that hides a body online, yet every square is laid by hand with a brush. From across the room the canvases read as a digital filter. Up close they are paintings, built one decision at a time.",
"Doxx's own reference is older than any screen: the mosaics of Pompeii, where small fragments were set to show the body openly. Her paintings hold both systems at once. The body is her own, and the grid that would normally conceal it is the very material it is made of. Whether the figure resolves depends on where the viewer stands.",
"In Gallery 4 the series hangs on the walls, while GLINA3 takes the room itself. Seven canvases, from 50 × 50 to 200 × 110 centimetres, their grid lines drawn in white, pink or orange, keep the visitor moving between distance and detail. That movement is part of the work."]

INBRIEF=[("Series","Pixelized Series, 2025–2026 · oil and acrylic on canvas · seven unique works"),
 ("Selected exhibitions","Shelter Amsterdam · Gallery BLNDSH, The Hague · NOCKNOCK Art Fair · Black Art Gallery"),
 ("Collaborations","Machine Gun Kelly · In Gold We Trust · Playboy (2025)")]
PORTRAIT_SRC="/home/claude/bd/raw/img-000.jpg"; PORTRAIT_CREDIT="Self-portrait"
