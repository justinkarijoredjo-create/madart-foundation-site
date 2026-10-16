# GLINA³ — Season 03 INLINE — Gallery 4
MAKER="GLINA³"; MAKER_H="GLINA&sup3;"; SLUG="glina3"
LOC="Fourth floor — Gallery 4"; GALLERY="Gallery 4"
SEASON="Season 03 — INLINE"
BASE="https://madartfoundation.com/"
WA_NUM="31657694723"
IG="glina__3"
WORKS=[dict(n=1,key="conditions-of-presence",title="Conditions of Presence",
  subtitle="An interactive column for body, time and place",
  medium="Aluminium extrusion, LED matrices, 3D-printed polymer and ceramic components, camera, proximity sensor, custom electronics, Python code and computational moving image",
  dims="Approx. 170 × 35 × 35 cm", year="2026",
  edition="Edition of 2 + 1 AP",
  extra="Edition of 2 + 1 AP · Approx. 60 kg · Live silhouette / no recording",
  price="€ 3.815,–", price_num=3815,
  img="/home/claude/gl/src/img-000.jpg",
  text=["Conditions of Presence is an interactive column composed of aluminium extrusion, LED matrices, sensors, a camera, custom electronics and computational moving image.",
   "The work brings together movement registered at radically different scales: archival experiments in computer animation, microscopic recordings of living systems and planetary imagery. A fourth layer belongs to the present encounter itself, exposing the computational system through which the visitor enters the work.",
   "As someone approaches, distance and presence begin to affect the image. The viewer is no longer positioned outside the work but becomes one of the conditions through which it exists.",
   "The installation treats the digital image not as immaterial content confined to a screen, but as part of a physical infrastructure of bodies, sensors, processors, electricity, code and matter.",
   "Conditions of Presence asks how presence is produced when human perception becomes entangled with the systems that sense, process and represent it."])]
for w in WORKS:
    w["code"]=f"INLINE-GL3-{w['n']:02d}"
    w["page"]=f"{SLUG}-{w['key']}"
    w["url"]=BASE+w["page"]+".html"
    w["meta"]=f"{w['medium']} · {w['dims']} · {w['year']}"
BIO=["GLINA³ is an Amsterdam-based creative technology, design and research studio founded by industrial designers Aleksandra Chargeishvili and Timo Bega, graduates of the Master Industrial Design programme at the Royal Academy of Art, The Hague.",
"Working across ceramic 3D printing, digital fabrication, computational design, electronics and research through making, the studio develops objects, interactive installations, surface systems and experimental production formats.",
"GLINA³ investigates how technologies usually encountered through screens, interfaces and machines can become physical, spatial and bodily experiences. Computation is treated not as an invisible tool behind the work, but as a condition that actively shapes form, behaviour and perception.",
"Our aim is to make emerging technologies more tactile, poetic and accessible. Through code, toolpaths, material behaviour, electronics, energy and human presence, GLINA³ explores how digital production can become part of everyday material culture."]
EXHIB="First prototype (two blocks), Gray Space in the Middle, The Hague, July 2026"
LEDE="An open aluminium column in which archival animation, living cells and planetary imagery share two LED screens — until someone steps close, and the image begins to include them."
WHY=[
 "INLINE asks what it means to make something in a world that always exists somewhere else too. Most of that elsewhere reaches us through a screen, and a screen is built to make its machinery disappear. GLINA³ do the opposite. In Conditions of Presence the aluminium frame stays open, the wiring stays visible, and the sensors and printed parts sit where anyone can see them. The image is still there; it no longer pretends to come from nowhere.",
 "On the two LED screens, four kinds of movement take turns: early computer animation from the archive of Doris Chase, microscopic recordings of living cells, NASA imagery, and a fourth layer that shows the system itself at work. The first three are movement recorded elsewhere, at scales the body cannot reach. The fourth needs a visitor. A camera and a proximity sensor register who comes near, and the image answers to that distance. Nothing is stored; the silhouette exists only while someone stands there.",
 "Aleksandra Chargeishvili and Timo Bega trained as industrial designers, and the column carries that training: modular, free-standing, made to be taken apart and put back together. In Gallery 4 it stands free in the room. Walk up to it — the work is only complete when someone does."]
