# MADART makerset data — ICONIC DESIGN OBJECTS × STUDIOSOPHIEHOSPES, Season 03 INLINE (Gallery Lounge)
MAKER="ICONIC DESIGN OBJECTS \u00d7 STUDIOSOPHIEHOSPES"
COVER=["ICONIC DESIGN OBJECTS","\u00d7 STUDIOSOPHIEHOSPES"]
SLUG="iconic-design-objects-studiosophiehospes"
INIT="IDSH"
CONTACT_FIRST="Lisa"; CONTACT_FULL="Lisa Wals"
WA_NUM="31612102158"
LOC="Fourth floor \u2014 Gallery Lounge"; GALLERY="Gallery Lounge"
SEASON="Season 03 \u2014 INLINE"
BASE="https://madartfoundation.com/"
RENDER="/mnt/user-data/uploads/Ultra_high-resolution_3D_rende_Nano_Banana_Pro_45869.jpg"
LINKS=[("Instagram \u2014 @iconicdesignobjects","https://www.instagram.com/iconicdesignobjects"),
       ("Instagram \u2014 @studiosophiehospes","https://www.instagram.com/studiosophiehospes"),
       ("Website \u2014 iconicdesignobjects.com","https://www.iconicdesignobjects.com"),
       ("Website \u2014 studiosophiehospes.com","https://www.studiosophiehospes.com")]
WORKS=[dict(n=1,key="ghost",title="Ghost",medium="Polished chrome & black",
    dims="18 \u00d7 14 \u00d7 25 cm (w \u00d7 d \u00d7 h)",year=None,
    extra="Edition of 50, numbered & signed",
    price="\u20ac 250,\u2013",price_num=250,vat=None,
    text=["A ghost is what remains when the object is gone.",
          "Ghost of Adolescence is about the years between childhood and adulthood, when you still look at the world with wonder and hold your dreams a little too tightly. Developed as collaboration between ICONIC DESIGN OBJECTS & STUDIOSOPHIEHOSPES, the figure stays in that in-between and refuses to grow out of it. Silver on the outside, black at the core, both finished to a high gloss."])]
for w in WORKS:
    w["code"]=f"INLINE-{INIT}-{w['n']:02d}"
    w["page"]=f"{SLUG}-{w['key']}"
    w["url"]=BASE+w["page"]+".html"
    w["meta"]=" \u00b7 ".join(x for x in (w["medium"],w["dims"],w["year"]) if x)
# Maker texts — verbatim as supplied (language points reported, not corrected)
IDO=["I-DO is a design and production company with offices in Amsterdam and Shenzhen, founded in 2022 by collectors who wanted to make the objects they were looking for themselves. We design and produce characters, sculptures, art collectibles and installations, from the first sketch to the finished piece.",
     "Our goal is to bring collectible art out of its niche and into everyday life, as something you own, experience and identify with. We build our own characters and the world around them, and we help artists and brands develop their IP into objects and experiences that people want to have. Everything we make is designed in Amsterdam and produced under our own supervision."]
SSH=["STUDIOSOPHIEHOSPES (SSH) is a creative studio based in Sweden focussed on creating campaigns, product design and digital brand worlds that bring together visual culture, innovation and performance.",
     "Combining design and emerging technology the studio explores the future of creativity across physical and digital spaces. Recent work includes projects for Nike, Ray-Ban and Mercer Labs (Museum of Art and Technology in New York)."]
LEDE="A figure that stays between childhood and adulthood and refuses to grow out of it: polished chrome on the outside, black at the core, in a numbered edition of fifty."
WHY=["INLINE asks what it means to make something in a world that always exists somewhere else too. A character is a clear case. Before Ghost was an object it was a sketch and a render, developed between an Amsterdam company that builds its own characters and the world around them, and a Swedish studio that works across physical and digital spaces. The object in the room is one appearance of the figure, not its origin.",
     "The makers describe Ghost as a figure of the years between childhood and adulthood \u2014 the period when much of what we hold on to is still imagined. The finish carries that idea. Silver on the outside, black at the core, both polished to a high gloss: the surface returns the room and whoever leans in, while the core stays dark. An edition of fifty, numbered and signed, lets the same figure exist in many places at once without becoming any less particular.",
     "I-DO began with collectors who wanted to make the objects they were looking for themselves, and that is the position they bring to the Gallery Lounge, the season\u2019s only duo. Ghost is shown at twenty-five centimetres, the scale of something kept close \u2014 made, in I-DO\u2019s own words, to be owned, experienced and identified with."]
IN_BRIEF=["I-DO \u2014 offices in Amsterdam and Shenzhen, founded 2022.",
          "STUDIOSOPHIEHOSPES \u2014 recent work includes projects for Nike, Ray-Ban and Mercer Labs (Museum of Art and Technology in New York)."]
# Collaboration image (option 1) + maker portraits, Buro Berger pattern
SILHOUETTE="/mnt/user-data/uploads/_ESRGAN_10409.jpg"
PEOPLE=[dict(key="ido",name="ICONIC DESIGN OBJECTS (I-DO)",short="I-DO",src="/mnt/user-data/uploads/PHOTO-2026-10-18-17-19-30.jpg",
             text=IDO,links=[("@iconicdesignobjects","https://www.instagram.com/iconicdesignobjects"),("iconicdesignobjects.com","https://www.iconicdesignobjects.com")]),
        dict(key="ssh",name="STUDIOSOPHIEHOSPES (SSH)",short="STUDIOSOPHIEHOSPES",src="/mnt/user-data/uploads/Scherm_afbeelding_2026-10-09_om_02_21_02.png",
             text=SSH,links=[("@studiosophiehospes","https://www.instagram.com/studiosophiehospes"),("studiosophiehospes.com","https://www.studiosophiehospes.com")])]
