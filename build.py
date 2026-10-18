#!/usr/bin/env python3
"""
MADART FOUNDATION — static site generator

    python3 build.py            build into ./build
    python3 build.py --check    build, then verify no existing URL disappeared

Everything the site says lives in ./data. Everything it looks like lives in
./templates and ./static. Nothing is edited by hand in ./build.

Rule that outranks all others: an artwork URL never changes. Physical QR codes
in the gallery point at these files. --check enforces it against urls.lock.
"""

import collections, hashlib, json, os, re, shutil, sys
from datetime import date
from pathlib import Path
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).parent
DATA, TPL, STATIC, OUT = ROOT/"data", ROOT/"templates", ROOT/"static", ROOT/"build"
ASSETS = ROOT/"assets"          # images, copied through untouched
LOCK = ROOT/"urls.lock"

TODAY = __import__("datetime").date.today().isoformat()

# old name -> new name. The old one is rebuilt as a redirect, never removed.
RENAMED = {
    "shop.html": "works.html",
    "missie.html": "mission.html",
    "pers.html": "press.html",
    "seizoen-01-paradox.html": "season-01-paradox.html",
    "seizoen-02-ground.html": "season-02-ground.html",
    "seizoen-03-inline.html": "season-03-inline.html",
    # Een maker heeft een pagina, niet een per seizoen. Het Curatorial-project
    # bouwde voor INLINE een tweede pagina voor drie makers die hier al stonden.
    # Die namen blijven bestaan als doorverwijzing, zodat elke link en elke
    # gedrukte QR die ernaar wijst blijft werken.
    "inline-aad-kruiswijk.html": "aad-kruiswijk.html",
    "devoonsounds-inline.html": "devoonsounds.html",
    "inline-dot-objects.html": "dot-objects.html",
    # Hetzelfde werk, eerder getoond in Maison d'Artiste en nu in INLINE. Een
    # werk heeft een pagina; de code daarop volgt het meest recente seizoen.
    # De INLINE-adressen blijven bestaan als doorverwijzing.
    "devoonsounds-inline-drop.html": "devoonsounds-devoon-drop.html",
    "devoonsounds-inline-original-1.html": "devoonsounds-original-1.html",
    "devoonsounds-inline-original-2.html": "devoonsounds-original-2.html",
    "devoonsounds-inline-original-3.html": "devoonsounds-original-3.html",
    "devoonsounds-inline-original-4.html": "devoonsounds-original-4.html",
    "inline-dot-objects-grid-shelving-unit-stainless-steel.html":
        "dot-objects-grid-shelving-unit-stainless-steel.html",
    **{f"inline-aad-kruiswijk-{k}.html": f"aad-kruiswijk-{k}.html"
       for k in ("m15-mdf", "m15-rvs", "m15-stadshout", "m16-i", "m16-ii",
                 "m18", "m19", "pouf")},
}

DAYS = [("mon","Monday"),("tue","Tuesday"),("wed","Wednesday"),("thu","Thursday"),
        ("fri","Friday"),("sat","Saturday"),("sun","Sunday")]


def load():
    site_doc = yaml.safe_load((DATA/"site.yaml").read_text())
    return {
        "site":    site_doc["site"],
        "seasons": site_doc["seasons"],
        "events":  site_doc["events"],
        "campaign": site_doc.get("campaign") or {},
        "maison":  site_doc["maison"],
        "giving":  site_doc["giving"],
        "plans":   yaml.safe_load((DATA/"plans.yaml").read_text(encoding="utf-8"))
                   if (DATA/"plans.yaml").exists() else {},
        "programme": yaml.safe_load((DATA/"programme.yaml").read_text(encoding="utf-8"))
                     if (DATA/"programme.yaml").exists() else {},
        "friend":  site_doc["friend"],
        "place":   site_doc["place"],
        "team":    site_doc["team"],
        "partners_upcoming": site_doc["partners_upcoming"],
        "programme_events": site_doc["programme_events"],
        "echo_members": yaml.safe_load((DATA/"echo_members.yaml").read_text()),
        "makers":  yaml.safe_load((DATA/"makers.yaml").read_text()),
        "works":   yaml.safe_load((DATA/"works.yaml").read_text()),
        "pages":   yaml.safe_load((DATA/"pages.yaml").read_text()),
        "building": yaml.safe_load((DATA/"building.yaml").read_text()),
    }


def _in_woorden(n):
    """Aantallen in de lopende tekst worden uitgeschreven, niet als cijfer.
    Stond eerder hardgecodeerd als "thirteen"; dat liep stil uit de pas zodra
    er een ECHO-maker bijkwam."""
    woorden = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six",
               7: "seven", 8: "eight", 9: "nine", 10: "ten", 11: "eleven",
               12: "twelve", 13: "thirteen", 14: "fourteen", 15: "fifteen",
               16: "sixteen", 17: "seventeen", 18: "eighteen", 19: "nineteen",
               20: "twenty"}
    return woorden.get(n, str(n))


def money(n):
    return "€ " + f"{n:,}".replace(",", ".") + ",–"


def enrich(d):
    """Derive everything the templates need, so templates stay dumb."""
    makers, works = d["makers"], d["works"]

    # Rename before anything is written, or pages built earlier in the run keep
    # pointing at the old slug.
    for s in d["seasons"]:
        s["slug"] = RENAMED.get(s["slug"] + ".html", s["slug"] + ".html")[:-5]

    for member in d["echo_members"]:
        shown = [works[s] for s in member["works"] if s in works and works[s].get("image")]
        member["portrait"] = f"portrait-echo-{member['slug']}.jpg"
        member["hover"] = (shown[0].get("thumb") or shown[0]["image"]) if shown else None
        member["work_count"] = len(member["works"])

    # Het collectiefblok op echo.html las een eigen ledenlijst uit makers.yaml.
    # Die liep stil achter zodra er een maker aan echo_members.yaml werd
    # toegevoegd: de nieuwe maker kreeg wel een pagina en stond wel in de
    # carrousel onderaan, maar niet in het blok "The collective". Een lijst is
    # de waarheid; de rest leidt eruit af.
    if "echo" in makers:
        makers["echo"]["members"] = [x["slug"] for x in d["echo_members"]
                                     if x["slug"] in makers]

    for m in makers.values():
        m["first_name"] = (m["name"] or "").split()[0]
        # Een maker kan in meer dan een seizoen hebben gestaan. Wat geweest is
        # verdwijnt niet: zijn portfolio bij de Foundation is cumulatief.
        # "programme" blijft het lopende seizoen — dat bepaalt de eyebrow en
        # de zaal — en "programmes" is alles waarin hij heeft gestaan.
        m["programmes"] = list(dict.fromkeys(
            [m["programme"]] + list(m.get("also_in") or [])))
        m["programme_label"] = ("Season 03 — INLINE" if m["programme"] == "inline"
                                else "Season 02 — GROUND" if m["programme"] == "ground"
                                else "Maison d'Artiste — GLUE")
        bio = m.get("bio") or ""
        m["short_bio"] = (bio[:78].rsplit(" ", 1)[0] + "…") if len(bio) > 80 else bio

    for w in works.values():
        mk = makers.get(w["maker"] or "")
        w["maker_name"] = mk["name"] if mk else ""
        w["maker_first"] = mk["first_name"] if mk else "the maker"
        if w["price_eur"]:
            w["price_label"] = money(w["price_eur"])
        else:
            w["price_label"] = "Price on request"
        w["programme"] = mk["programme"] if mk else None
        w["programmes"] = list(mk.get("programmes") or [mk["programme"]]) if mk else []
        # The work page is the QR landing page: opened on a phone, in the
        # gallery, usually on mobile data. The photograph is never shown
        # wider than about 1100px there, so a screen-size rendition is used
        # when one exists. The original file stays in place and keeps its
        # URL — nothing that has been live disappears.
        img = w.get("image")
        w["image_screen"] = (f"w-{img}" if img and (ASSETS / f"w-{img}").exists()
                             else img)
        if mk and mk.get("kind") == "collective":
            w["sales_via"] = "Maaike Rabbinge"
        # Studio's en merken vallen buiten het programma van de Foundation.
        w["is_partner"] = bool(mk and mk.get("kind") == "partner")

    # Een maker kan op de ene verdieping autonoom werk tonen en op de andere
    # als ontwerper terugkomen. Dat verband staat aan beide kanten: op het werk
    # de naam van de ontwerper, en op zijn eigen pagina waar het te zien is.
    for slug, w in works.items():
        ds = w.get("designer_slug")
        if ds and ds in makers:
            makers[ds].setdefault("designed_for", []).append(
                {"title": w["title"], "href": f"{slug}.html",
                 "studio": makers[w["maker"]]["name"],
                 "studio_href": f"{w['maker']}.html"})
        s = (w["status"] or "").lower()
        # Verkocht is een eigen toestand: het werk blijft zichtbaar met zijn
        # eigen pagina — de QR-code in de galerie moet blijven werken — maar
        # het valt uit de lijst van beschikbare werken.
        if s == "sold":
            w["pill"], w["status"] = "sold", "sold"
        elif s == "available":
            w["pill"], w["status"] = "available", "available"
        else:
            w["pill"], w["status"] = "request", "on request"

    # Een werkcode staat op een gedrukt label en in een aanvraag per WhatsApp.
    # Twee werken met dezelfde code is dus niet slordig maar onbruikbaar: de
    # maker weet niet welk stuk bedoeld wordt. Bevinding C-02 was precies dit.
    _codes = collections.Counter(w.get("code") for w in works.values() if w.get("code"))
    _dubbel = {c: n for c, n in _codes.items() if n > 1}
    if _dubbel:
        for c, n in sorted(_dubbel.items()):
            wie = sorted({works[s]["maker"] for s in works if works[s].get("code") == c})
            print(f"  LET OP  werkcode {c} staat op {n} werken: {', '.join(wie)}")

    # a work belongs to a maker's catalogue; catch any that fell out of one
    listed = {s for m in makers.values() for s in m["works"]}
    for slug, w in works.items():
        if slug not in listed and w["maker"] in makers:
            makers[w["maker"]]["works"].append(slug)

    d["site"]["hours_json"] = json.dumps(d["site"]["hours"])

    # Een statische zin die altijd waar is, als bodem onder de live status.
    _h = d["site"]["hours"]
    _open = {tuple(v) for v in _h.values() if v}
    if len(_open) == 1 and len(_h) == 7:
        _a, _b, _c, _e = next(iter(_open))
        d["site"]["hours_static"] = f"Open daily {_a:02d}:{_b:02d}\u2013{_c:02d}:{_e:02d}"
    else:
        d["site"]["hours_static"] = "Opening hours"
    # Browsers cache the stylesheet. A fingerprint of its contents in the URL means
    # a changed stylesheet is a new URL, so nobody has to force-refresh.
    css = (STATIC/"style.css").read_bytes()
    d["site"]["asset_version"] = hashlib.sha1(css).hexdigest()[:8]
    return d


ORDER = {"current": 0, "upcoming": 1, "past": 2}

def clip(text, limit=155):
    """Een beschrijving afkappen op een woordgrens, niet midden in een woord.

    Google en linkpreviews tonen deze zin; hij hoort af te lopen. Eerst de
    laatste zin die nog past, anders de laatste hele woordgrens, met een
    beletselteken. Leestekens aan het eind worden opgeruimd."""
    t = re.sub(r"\s+", " ", (text or "")).strip()
    if len(t) <= limit:
        return t
    zin = re.search(r"^.{40,%d}[.!?](?=\s|$)" % limit, t)
    if zin:
        return zin.group(0).strip()
    kort = t[:limit - 1]
    kort = kort[:kort.rfind(" ")] if " " in kort else kort
    return kort.rstrip(" ,;:—-") + "\u2026"




def exhibition_rows(d):
    """What is on now, then what is coming, then what has been."""
    rows = []
    for s in d["seasons"]:
        rows.append({"kind": f"SEASON {s['number']}", "title": f"Season {s['number']} — {s['title']}",
                     "sub": s["standfirst"][:56].rsplit(" ", 1)[0] + "…", "location": s["location"],
                     "dates": s["dates_label"], "href": f"{s['slug']}.html", "status": s["status"],
                     "card": s.get("card")})
    # Maison d'Artiste EN GLUE Amsterdam 2026 stonden hier als twee kaarten met
    # dezelfde datums. Het is één ding: het festival van de Foundation, binnen
    # GLUE. Twee kaarten lieten een bezoeker denken dat het er twee waren, en
    # spraken de attributie tegen die elders op de site staat.
    md = d["maison"]
    ev = next((e for e in d["events"] if e["dates_label"] == md["dates_label"]), None)
    rows.append({"kind": (md.get("kind") or "exhibition").upper(), "title": md["title"],
                 "sub": md["subtitle"],
                 "location": ev["location"] if ev else md["location"],
                 "dates": md["dates_label"], "href": f"{md['slug']}.html",
                 "status": "current", "card": md.get("card")})
    for e in d["events"]:
        if ev and e is ev:
            continue
        rows.append({"kind": "EVENT", "title": e["title"], "sub": e["standfirst"][:56].rsplit(" ", 1)[0] + "…",
                     "location": e["location"], "dates": e["dates_label"], "href": "events.html",
                     "status": e["status"], "card": e.get("card")})
    # Op status, en binnen een status op datum. Zonder dat tweede sorteert
    # Python op invoervolgorde en stond Season 03 vóór Season 01 in de strook,
    # wat voor een bezoeker die het programma volgt niet te lezen is.
    def _start(r):
        m = re.search(r"(\d{4})", (r.get("dates") or ""))
        return int(m.group(1)) if m else 0
    rows.sort(key=lambda r: (ORDER.get(r.get("status"), 3),
                             -_start(r) if r.get("status") == "past" else _start(r)))
    return rows


ORDINAAL = {0: "Ground floor", 1: "First floor", 2: "Second floor", 3: "Third floor",
            4: "Fourth floor", 5: "Fifth floor", 6: "Sixth floor", 7: "Seventh floor"}


def plek(m, vorm="navigeren"):
    """Waar staat deze maker, geschreven naar de plek waar het staat.

    De vuistregel: het verdiepingsnummer wanneer iemand nog moet navigeren,
    de ruimtenaam wanneer hij er al is. Daarom staan verdieping en ruimte als
    losse velden in de gegevens en niet als een samengevoegde tekst; anders
    kun je ze niet per context anders tonen.

    vorm "navigeren"  ->  Fourth floor — Gallery 4        (programma, maker)
    vorm "ruimte"     ->  Gallery 4                       (plattegrond)
    vorm "kort"       ->  Fourth floor                    (lijsten)
    """
    v = m.get("floor")
    kamers = m.get("rooms") or []
    if v is None and not kamers:
        return ""
    def verdieping(x):
        if isinstance(x, list):
            return " / ".join(ORDINAAL.get(i, str(i)) for i in x)
        return ORDINAAL.get(x, str(x))
    if vorm == "ruimte":
        return " / ".join(kamers)
    if vorm == "kort" or not kamers:
        return verdieping(v)
    uit = verdieping(v) + " — " + " / ".join(kamers)
    if m.get("spot"):
        uit += " · " + m["spot"]
    return uit


def maker_meta(m, aantal, tot_datum):
    """De meta-description van een makerspagina.

    De makersnaam is voor bijna elke maker de enige zoekopdracht waarop deze
    site realistisch kan winnen — en dan moet het fragment iets bieden wat de
    eigen site van de maker niet biedt: dat het werk hier hangt, met hoeveel
    werken, en tot wanneer. De bio alleen zegt dat niet.
    """
    kern = clip(m.get("bio") or "", 74).rstrip(" .\u2026,")
    # Een fragment dat op een voegwoord eindigt leest als een afgebroken zin.
    LOS = {"and", "that", "with", "between", "from", "of", "the", "a", "an",
           "in", "on", "for", "to", "as", "by", "into", "moving"}
    while kern and kern.rsplit(" ", 1)[-1].lower() in LOS:
        kern = kern.rsplit(" ", 1)[0].rstrip(" ,\u2014-")
    if aantal:
        staart = ("%d work%s at MADART Foundation, NIO House Amsterdam, %s"
                  % (aantal, "" if aantal == 1 else "s", tot_datum))
    else:
        staart = "At MADART Foundation, NIO House Amsterdam, %s" % tot_datum
    return (kern + ". " + staart) if kern else staart


def teken_plan(pl, namen_per_ruimte=None):
    """Bouw de SVG van een verdiepingsplattegrond uit data/plans.yaml.

    De maten zijn millimeters uit de architectentekening, met het raster van
    NIO House als nulpunt. Alles wat je hier ziet is nagemeten, niet geschat:
    de contour, de zaalgrenzen, de liften, het trappenhuis en de vaste wand."""
    namen_per_ruimte = namen_per_ruimte or {}
    vloer = pl["outline"]
    xs = [q[0] for q in vloer]; ys = [q[1] for q in vloer]
    lifts = pl.get("lifts") or []; trap = pl.get("stairs")
    MX = min([min(xs)] + ([trap[0] - 1450] if trap else []))
    MY = min([min(ys)] + [2000])
    PAD = 1150
    VW = max(xs) - MX + PAD * 2
    VH = max(ys) - MY + PAD * 2 + 900
    def f(x, y): return (round(x - MX + PAD), round(y - MY + PAD))
    def pol(pts): return " ".join("%d,%d" % f(*q) for q in pts)

    muur = "".join('<line x1="%d" y1="%d" x2="%d" y2="%d"/>' % (f(*a) + f(*b))
                   for a, b in pl.get("wall", []))
    # De namen horen op de kaart, niet alleen in de lijst. Eén lettermaat voor
    # de hele verdieping: de grootste die in elke ruimte past, gegeven hoeveel
    # regels daar staan. Waar er meer dan vier namen zijn worden er vier
    # getoond met een telling erachter; vijf regels in een kamer van vijf meter
    # is op een telefoon niet meer te lezen.
    def kort(m):
        """Wat er van een naam op de kaart past.

        Een studio of collectief heet zoals het heet. Bij een persoon valt de
        voornaam weg, met tussenvoegsel: Anne van Borselen wordt VAN BORSELEN,
        niet BORSELEN, en Maurice Albert Jan wordt ALBERT JAN en niet JAN.
        Wordt het dan nog te lang, dan blijft de eerste achternaam over."""
        naam = m["name"]
        if m.get("kind") in ("partner", "collective") or " " not in naam:
            return naam.upper()
        rest = naam.split(" ", 1)[1]
        if "&" in rest:
            rest = rest.split("&")[0].strip()
        if len(rest) > 12:
            rest = rest.split()[-1]
        if len(rest) > 12 and "-" in rest:
            rest = rest.split("-")[0]
        return rest.upper()

    def korter(m):
        """De krappe vorm, voor een kamer waar de volle naam niet in past."""
        naam = m["name"]
        if m.get("kind") in ("partner", "collective") or " " not in naam:
            return naam.upper()
        laatste = naam.split("&")[0].split()[-1]
        return (laatste.split("-")[0] if len(laatste) > 12 else laatste).upper()

    # Wie door de hele verdieping verspreid staat hoort niet in elke kamer
    # herhaald te worden; dat maakt vier kamers vol met dezelfde twee namen.
    overal_slugs = set((pl.get("everywhere") or {}).keys())
    inhoud = {naam: [kort(m) for m in (namen_per_ruimte.get(naam) or [])
                     if m["slug"] not in overal_slugs]
              for naam in pl["rooms"]}

    def maat_voor(naam, r):
        straal = r["label"].get("r", 1500)
        wie = inhoud[naam]
        # Meten op de tekst die er werkelijk komt te staan, niet op de volle
        # naam: waar een korte naam is opgegeven is dat wat de ruimte draagt.
        toon = r.get("short_name") or naam
        regels = (1 + len(wie)) if wie else 1
        langste = max([len(toon)] + [len(w) for w in wie])
        op_breedte = (2 * straal * 0.86) / (langste * 0.60)
        op_hoogte = (2 * straal * 0.86) / (regels * 1.20)
        return min(op_breedte, op_hoogte)
    # De maat per ruimte, niet per verdieping. Op verdieping 6 verschillen de
    # kamers sterk in grootte en in aantal namen; een gedeelde maat wordt dan
    # gedicteerd door de krapste kamer en daar wordt de hele verdieping klein
    # van. Per ruimte rekenen laat de grote kamers groot en houdt de kleine
    # leesbaar. De band is smal, zodat het verschil als verhouding leest en
    # niet als slordigheid.
    # Past de volle vorm niet ruim, dan wijkt die kamer uit naar de krappe.
    # Zo blijft de letter leesbaar in plaats van dat de naam over de wand loopt.
    for naam in pl["rooms"]:
        if maat_voor(naam, pl["rooms"][naam]) < 470 and inhoud[naam]:
            inhoud[naam] = [korter(m) for m in (namen_per_ruimte.get(naam) or [])
                            if m["slug"] not in overal_slugs]
    # Blijft het daarna nog onder de leesbaarheidsdrempel, dan vallen de namen
    # in die ruimte helemaal weg. Beter alleen de ruimtenaam dan een naam die
    # over de wand loopt of vier pixels hoog is.
    # En als het in een van de ruimtes niet past, vallen de namen op de hele
    # verdieping weg. Een plattegrond waarop de ene kamer namen draagt en de
    # buurkamer niet leest als een fout, niet als een keuze.
    if any(inhoud[n] and maat_voor(n, pl["rooms"][n]) < 400 for n in pl["rooms"]):
        inhoud = {n: [] for n in pl["rooms"]}
    maten = {n: maat_voor(n, r) for n, r in pl["rooms"].items()}
    top = min(660, max(maten.values()))
    def maat_van(n):
        return int(max(400, min(top, maten[n])))

    zalen = []
    for i, (naam, r) in enumerate(pl["rooms"].items(), start=1):
        lab = r["label"]
        cx, cy = f(lab["x"], lab["y"])
        wie = inhoud[naam]
        maat = maat_van(naam); klein = int(maat * 0.62)
        toon = (r.get("short_name") or naam).upper()
        if not wie:
            t = '<text class="naam" font-size="%d" x="%d" y="%d">%s</text>' % (
                maat, cx, round(cy + maat * 0.34), toon)
        else:
            hoog = klein * 1.35 + len(wie) * maat * 1.18
            y0 = cy - hoog / 2 + klein
            t = '<text class="zaalregel" font-size="%d" x="%d" y="%d">%s</text>' % (
                klein, cx, round(y0), toon)
            for k, w in enumerate(wie):
                t += '<text class="naam" font-size="%d" x="%d" y="%d">%s</text>' % (
                    maat, cx, round(y0 + klein * 0.55 + maat * 1.12 * (k + 1)), w)
        zalen.append(
            '<g class="zaal" id="room-%d" data-z="%d" tabindex="0" role="button" '
            'aria-label="%s"><polygon class="vlak" points="%s"/><g class="tag">%s</g></g>'
            % (i, i, naam, pol(r["shape"]), t))

    def lift(q):
        x, y = f(*q)
        return ('<rect x="%d" y="%d" width="1560" height="1700" rx="80"/>' % (x - 780, y - 850) +
                '<path class="pijl" d="M%d %d l330 -420 l330 420 z M%d %d l330 420 l330 -420 z"/>'
                % (x - 330, y - 160, x - 330, y + 160))
    kern = '<g class="kern" aria-hidden="true">' + "".join(lift(q) for q in lifts)
    label = ""
    if lifts:
        mx = sum(f(*q)[0] for q in lifts) // len(lifts)
        label += '<text x="%d" y="%d">LIFTS</text>' % (mx, f(*lifts[0])[1] - 1150)
    if trap:
        tx, ty = f(*trap)
        kern += '<rect x="%d" y="%d" width="2600" height="5400" rx="80"/>' % (tx - 1300, ty - 2700)
        kern += '<g class="tredes">' + "".join(
            '<line x1="%d" y1="%d" x2="%d" y2="%d"/>' % (tx - 1300, ty - 2700 + i * 540,
                                                        tx + 1300, ty - 2700 + i * 540)
            for i in range(1, 10)) + "</g>"
        label += '<text x="%d" y="%d">STAIRWELL</text>' % (tx, ty - 3150)
    kern += "</g>" + ('<g class="kernlabel">%s</g>' % label if label else "")

    buiten = ""
    for k, o in enumerate(pl.get("outside", []), start=len(pl["rooms"]) + 1):
        ox, oy = f(*o["at"])
        buiten += ('<g class="zaal herma" id="room-%d" data-z="%d" tabindex="0" role="button" '
                   'aria-label="%s, %s">'
                   '<rect x="%d" y="%d" width="4200" height="1700" fill="transparent"/>'
                   '<circle class="stip" cx="%d" cy="%d" r="330"/>'
                   '<text x="%d" y="%d" text-anchor="middle">%s</text></g>'
                   % (k, k, o["name"], o.get("note", ""), ox - 1600, oy - 400, ox, oy,
                      ox + 620, oy + 950, o["name"].upper()))
    st = pl.get("streets") or {}
    straat = ""
    if st:
        straat = '<g class="straat" aria-hidden="true">'
        if st.get("bottom"):
            straat += '<text x="%d" y="%d">%s</text>' % (
                f(9000, 0)[0], f(0, max(ys))[1] + 820, st["bottom"].upper())
        if st.get("right"):
            rx, ry = f(max(xs), 9000)
            straat += ('<text transform="rotate(90 %d %d)" x="%d" y="%d">%s</text>'
                       % (rx + 780, ry, rx + 780, ry, st["right"].upper()))
        straat += "</g>"
    return ('<svg viewBox="0 0 %d %d" xmlns="http://www.w3.org/2000/svg" class="plan" role="img" '
            'aria-label="Plan of %s">'
            '<defs><filter id="diepte" x="-10%%" y="-10%%" width="125%%" height="125%%">'
            '<feDropShadow dx="0" dy="150" stdDeviation="190" flood-color="#1E1D1C" flood-opacity=".13"/>'
            '</filter></defs>%s<g filter="url(#diepte)"><polygon class="romp" points="%s"/></g>'
            '<g class="zalen">%s</g><g class="muur" aria-hidden="true">%s</g>'
            '<polygon class="omtrek" points="%s"/>%s%s</svg>'
            % (VW, VH, pl["label"], kern, pol(vloer), "".join(zalen), muur, pol(vloer),
               buiten, straat))


def build():
    d = enrich(load())

    # Elke maker krijgt zijn plek in twee vormen mee: de navigeervorm voor
    # lijsten en pagina's, de ruimtevorm voor de plattegrond.
    for _m in d["makers"].values():
        _m["plek"] = plek(_m)
        _m["plek_ruimte"] = plek(_m, "ruimte")
        _m["plek_kort"] = plek(_m, "kort")

    # De plattegronden bepalen welke knoppen er mogen zijn. Dit moet vóór het
    # schrijven van welke pagina dan ook, anders wijst de homepage naar een
    # plattegrond die nog niet bestaat.
    plannen = d.get("plans") or {}
    camp = d.get("campaign") or {}
    plan_links = {str(k): 1 for k in plannen}
    for lid, lv in d["building"]["programme"]["levels"].items():
        if lv.get("plan") and str(lid) not in plan_links:
            lv["plan"] = None
    site, makers, works = d["site"], d["makers"], d["works"]
    env = Environment(loader=FileSystemLoader(TPL), autoescape=select_autoescape(["html"]),
                      trim_blocks=True, lstrip_blocks=True)

    def _adressen(tekst):
        """Een e-mailadres in lopende tekst is op een telefoon niet aan te
        tikken; een journalist met een deadline moet het dan overtypen."""
        from markupsafe import Markup, escape
        uit = str(escape(tekst))
        uit = re.sub(r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-z]{2,})",
                     r'<a href="mailto:\1">\1</a>', uit)
        return Markup(uit)

    env.filters["adressen"] = _adressen

    OUT.mkdir(exist_ok=True)
    for f in OUT.glob("*.html"):
        f.unlink()

    season = next(s for s in d["seasons"] if s["status"] == "current")
    event = next((e for e in d["events"] if e["status"] == "current"), None)
    rows = exhibition_rows(d)

    maker_list = sorted(makers.values(), key=lambda m: m["name"])
    artists = [m for m in maker_list if m.get("category") == "artist"]
    collectives_ = [m for m in maker_list if m.get("category") == "collective"]
    partners_ = [m for m in maker_list if m.get("category") == "partner"]
    # De teller is cumulatief over alles wat de Foundation zelf heeft gecureerd.
    # Seizoen 01 PARADOX telt niet mee: dat liep onder een ander model, met
    # galeries die de ruimte huurden en hun eigen makers vertegenwoordigden,
    # voordat de Foundation bestond. De regel staat in data/site.yaml, zodat
    # een volgend seizoen daar wordt aangezet en niet hier.
    curated_programmes = {x.get("programme") for x in d["seasons"]
                          if x.get("curated_by_foundation")} | {"maison", "stairwells", "talks"}
    curated = [m for m in artists if m.get("programme") in curated_programmes]
    maison = [m for m in curated if set(m["programmes"]) & {"maison", "stairwells", "talks"}]
    collectives = collectives_
    partners = partners_

    def _kaartbeeld(w):
        # h- is de lichte uitsnede die de kaart normaal toont; die bestaat maar
        # voor een handvol werken. t- is het alternatief, anders het origineel.
        basis = w.get("image")
        if basis and (ASSETS / ("h-" + basis)).exists():
            return "h-" + basis
        return w.get("thumb") or basis

    # Elke merkkaart op makers.html toont bij hover een werk van dat merk. Welk
    # werk is per bezoek anders; dit is de voorraad waaruit gekozen wordt.
    for _p in partners_:
        _p["hover_pool"] = [b for b in (_kaartbeeld(works[s])
                                        for s in _p.get("works", []) if s in works) if b]
    ground = [m for m in curated if "ground" in m["programmes"]]
    glue = maison

    work_list = sorted(works.values(), key=lambda w: (w["maker_name"], w["title"] or ""))
    featured = [w for w in work_list if w["image"] and w["price_eur"]][:8]

    works_json = json.dumps([{k: w[k] for k in
        ("slug","title","maker","maker_name","image","materials","code","status","pill","price_label")}
        | {"thumb": w.get("thumb"), "width": w.get("width"), "height": w.get("height")}
        | {"price": w["price_eur"]} for w in work_list if w["image"]], ensure_ascii=False)

    common = dict(site=site, seasons=d["seasons"], events=d["events"],
                  makers=maker_list, works=work_list, season=season, event=event,
                  building=d["building"])

    def write(name, template, **ctx):
        ctx_full = {**common, **ctx, "page_path": name}
        html = env.get_template(template).render(**ctx_full)
        (OUT/name).write_text(html, encoding="utf-8")

    # De drie meest recente publicaties op de homepage; de rest op press.html.
    _dek = (d["pages"].get("pers") or {}).get("coverage") or []
    write("index.html", "home.html", dekking=_dek[:3],
          page_title="Contemporary makers, curated in Amsterdam",
          page_description=site["description"], og_image=season["hero"],
          makers_solo=artists, artists=artists, curated=curated,
          echo=(collectives[0] if collectives else None),
          echo_members=d["echo_members"], featured_works=featured,
          # De teller telt het register, en dat is wat de werkenpagina toont:
          # het werk van de makers. Het werk van de merkpartners staat in het
          # huis maar niet in het register.
          works_shown=[w for w in work_list if w["image"]
                       and makers.get(w["maker"], {}).get("kind") != "partner"],
          site_place=d["place"], team=d["team"],
          # Het festivalblok op de homepage verschijnt alleen zolang het
          # festival loopt of eraan komt. Na de laatste dag valt het weg
          # zonder dat er iemand aan hoeft te denken.
          festival_nu=next((e for j, e in sorted((d.get("programme") or {}).items())
                            if date.today() <= date(2026, 9, 19)), None),
          collectives=collectives_, programme_events=d["programme_events"],
          exhibition_cards=[dict(r, image=r.get("card")) for r in rows
                            if r["kind"] not in ("EVENT", "FESTIVAL")])

    # ---- Maison d'Artiste, het festival --------------------------------
    # De ticketlinks van de vier talks staan al in data/building.yaml; die
    # worden hier gekoppeld zodat ze maar op een plek onderhouden worden.
    tickets = {}
    for lvl in d["building"]["programme"]["levels"].values():
        for g in lvl.get("groups") or []:
            for x in g.get("people") or []:
                if x.get("external"):
                    tickets[x["name"]] = x["external"]

    ORD = {0: "Ground floor", 1: "First floor", 2: "Second floor", 4: "Fourth floor",
           5: "Fifth floor", 6: "Sixth floor", 7: "Seventh floor"}
    for jaar, ed in (d.get("programme") or {}).items():
        zonder = []
        for dag in ed["days"]:
            for it in dag["items"]:
                mk_ = makers.get(it.get("maker") or "")
                # Een spreker is geen maker: die heeft geen pagina maar wel een
                # kaartje. Zoek het adres op de naam zoals die in building.yaml
                # staat, zodat het op een plek onderhouden wordt.
                naam = it.get("speaker") or (mk_ and mk_["name"])
                if not it.get("book_url") and naam and tickets.get(naam):
                    it["book_url"] = tickets[naam]
                if it.get("maker") and mk_:
                    it["maker_name"] = mk_["name"]
                    it["maker_page"] = None if mk_.get("pending") else it["maker"] + ".html"
                waar = ORD.get(it.get("floor")) if it.get("floor") is not None else None
                if waar and it.get("room"):
                    waar += " — " + it["room"]
                it["waar"] = waar or it.get("room") or ""
                # De verdieping staat er al; die kan de link naar de
                # plattegrond zijn. Wie het programma leest en wil weten waar
                # The Conservatory is, hoeft dan niet twee stappen terug.
                vl = it.get("floor")
                it["plan"] = f"plan-{vl}.html" if vl in plannen else None
                if it["status"] == "book" and not it.get("book_url"):
                    zonder.append(it["anchor"])
        # Een maker die een talk geeft krijgt hem op zijn eigen pagina, uit
        # dezelfde bron. Zo staat de tekst maar op een plek.
        for dag in ed["days"]:
            for it in dag["items"]:
                sl = it.get("maker")
                # Elke maker met een programmaonderdeel krijgt het blok op zijn
                # eigen pagina. Dat stond aan voor twee van de vijf, wat betekende
                # dat wie via Google op Inge Bečka binnenkwam achttien werken zag
                # en geen enkele reden om op 17 september langs te komen.
                # Een maker kan meer dan een onderdeel geven: Inge Bečka doet
                # twee artist talks, en aan de Table Talk zitten er drie.
                # Daarom een lijst, niet een enkel blok.
                for sl2 in ([sl] if sl else []) + (it.get("speakers") or []):
                    if sl2 not in makers:
                        continue
                    makers[sl2].setdefault("talks", []).append({
                        "title": it["title"], "when": dag["label"] + " 2026 · " + it["time"],
                        "waar": it["waar"], "body": it.get("body"), "body2": it.get("body2"),
                        "language": it.get("language"), "places": it.get("places"),
                        "book_url": it.get("book_url"), "anchor": it["anchor"],
                        "programme": ed["slug"] + ".html"})
        ed["jaar"] = jaar
        if zonder:
            print(f"  LET OP  {len(zonder)} onderdelen van Maison d'Artiste {jaar} hebben nog"
                  f" geen boekingsadres: {', '.join(zonder)}")
        # M-02 — de programmapagina droeg geen gestructureerde data, terwijl
        # dit de enige pagina is met echte evenementen erop. Zonder Event-
        # markering komt geen enkel onderdeel in aanmerking voor de
        # evenementenresultaten van een zoekmachine, en dat is een opbrengst
        # die na 19 september niet meer te halen is.
        DATUM = {"do": "2026-09-17", "vr": "2026-09-18", "za": "2026-09-19"}
        plaats = {"@type": "Place", "name": site["venue"]["name"],
                  "address": {"@type": "PostalAddress",
                              "streetAddress": "Leidsestraat 32-34",
                              "postalCode": "1017 PB", "addressLocality": "Amsterdam",
                              "addressCountry": "NL"}}
        basis = f"{site['url'].rstrip('/')}/{ed['slug']}.html"
        graaf = [{"@type": "Festival", "@id": basis + "#festival", "name": ed["title"],
                  "startDate": "2026-09-17T10:00+02:00",
                  "endDate": "2026-09-19T18:00+02:00",
                  "eventStatus": "https://schema.org/EventScheduled",
                  "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
                  "location": plaats, "url": basis,
                  # Het festival is gratis toegankelijk; dat hoort in de
                  # gegevens te staan, want "free entry" is precies wat iemand
                  # in een zoekresultaat wil zien.
                  "description": ("Three days in the Metzgebouw during GLUE Amsterdam. "
                                  "Thirty makers across eight levels, talks, tours and "
                                  "sound in Rietveld's dome. Free entry."),
                  "image": f"{site['url'].rstrip('/')}/{ed['og_image']}" if ed.get("og_image") else None,
                  "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR",
                             "availability": "https://schema.org/InStock", "url": basis},
                  "organizer": {"@type": "NGO", "name": site["name"],
                                "url": site["url"]},
                  # GLUE stond hier als geneste Event met alleen een naam. Een
                  # Event zonder datum en locatie is ongeldig, en Google telde
                  # hem als zevenentwintigste item. Nu volledig.
                  "superEvent": {"@type": "Festival", "name": "GLUE Amsterdam",
                                 "startDate": "2026-09-17T10:00+02:00",
                                 "endDate": "2026-09-19T18:00+02:00",
                                 "url": "https://glue.amsterdam/",
                                 "location": {"@type": "Place", "name": "Amsterdam",
                                              "address": {"@type": "PostalAddress",
                                                          "addressLocality": "Amsterdam",
                                                          "addressCountry": "NL"}}}}]
        for dag in ed["days"]:
            for it in dag["items"]:
                begin, eind = [x.strip() for x in it["time"].replace("\u2013", "-").split("-")]
                # Een aanbod zonder werkende route is geen aanbod. PreOrder
                # vraagt bovendien om een validFrom die we niet hebben, en dat
                # is precies wat Google ongeldig noemt. Waar niet geboekt kan
                # worden, laten we het aanbod weg.
                offer = None
                if it["status"] in ("free", "invitation"):
                    offer = {"@type": "Offer", "priceCurrency": "EUR", "price": "0",
                             "availability": "https://schema.org/InStock",
                             "url": basis + "#" + it["anchor"]}
                elif it.get("book_url") and it.get("price_high"):
                    # Meer dan een prijs: voorverkoop, regulier, aan de deur.
                    # Een enkele prijs zou Google een bedrag laten tonen dat
                    # maar voor een deel van de kaartjes geldt.
                    offer = {"@type": "AggregateOffer", "priceCurrency": "EUR",
                             "lowPrice": str(it["price_eur"]),
                             "highPrice": str(it["price_high"]),
                             "availability": "https://schema.org/InStock",
                             "url": it["book_url"]}
                elif it.get("book_url"):
                    offer = {"@type": "Offer", "priceCurrency": "EUR",
                             "price": str(it.get("price_eur") or 0),
                             "availability": "https://schema.org/InStock",
                             "url": it["book_url"]}
                ev = {"@type": "Event", "name": it["title"],
                      "startDate": f"{DATUM[dag['id']]}T{begin}+02:00",
                      "endDate": f"{DATUM[dag['id']]}T{eind}+02:00",
                      "eventStatus": "https://schema.org/EventScheduled",
                      "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
                      "location": plaats,
                      "organizer": {"@type": "NGO", "name": site["name"],
                                    "url": site["url"]},
                      "superEvent": {"@id": basis + "#festival"},
                      "url": basis + "#" + it["anchor"]}
                if offer:
                    ev["offers"] = offer
                # De omschrijving nam alleen de eerste alinea. Bij een tekst
                # die met een korte regel opent — "An invitation to move, then
                # rest." — bleef er niets over om een zoekresultaat mee te
                # vullen. Nu de alinea's aan elkaar, tot de limiet.
                _oms = " ".join(x for x in (it.get("body"), it.get("body2"),
                                            it.get("body3")) if x)
                if _oms:
                    ev["description"] = clip(_oms, 240)
                if it.get("who"):
                    ev["performer"] = {"@type": "Person", "name": it["who"]}
                if ed.get("og_image"):
                    ev["image"] = f"{site['url'].rstrip('/')}/{ed['og_image']}"
                graaf.append(ev)
        graaf = [{k: v for k, v in kn.items() if v is not None} for kn in graaf]
        ed["jsonld"] = json.dumps({"@context": "https://schema.org", "@graph": graaf},
                                  ensure_ascii=False)

        write(f"{ed['slug']}.html", "programme.html", camp=camp,
              page_title=ed["title"] + " \u2014 eight floors during GLUE Amsterdam",
              page_description=("Three days in the Metzgebouw during GLUE Amsterdam. Thirty makers "
                                "across eight levels, talks, tours and sound in Rietveld's dome. "
                                "17–19 September, free entry."),
              og_image=ed.get("og_image"), editie=ed)
        # de Table Talk krijgt een eigen pagina: het is het onderdeel dat het
        # verhaal van de Foundation draagt en apart uitgespeeld wordt
        tt = next((i for dag in ed["days"] for i in dag["items"]
                   if i["anchor"] == "do-table-talk"), None)
        if tt:
            write("madart-table-talk.html", "tabletalk.html",
                  page_title="MADART Table Talk",
                  page_description=("Three makers at ignore's table on the sixth floor, Thursday "
                                    "17 September. None of them arrived the way the art world "
                                    "expects."),
                  og_image=ed.get("og_image"), item=tt, editie=ed, makers=makers)

    # ---- de plattegronden -------------------------------------------------
    # Wie in welke zaal staat komt uit het locatieveld van de maker, niet uit
    # een lijst hier. Verhuist iemand, dan verandert data/makers.yaml en klopt
    # de plattegrond mee.
    # Waar hangt dit werk? Van het werk naar de maker naar de zaal, en van de
    # zaal naar het adres op de plattegrond. Zo sluit de QR-code in de galerie
    # de kring: van het werk naar de plek, en van de plek naar de buren.
    def in_ruimte(m, naam):
        """Staat deze maker in deze ruimte? Nu een vergelijking van velden,
        niet van tekst."""
        return naam in (m.get("rooms") or [])

    zaal_adres = {}
    for nummer, pl in plannen.items():
        for i, naam in enumerate(pl["rooms"], start=1):
            zaal_adres[naam] = (f"plan-{nummer}.html#room-{i}", pl["label"], naam)
        for k, o in enumerate(pl.get("outside", []), start=len(pl["rooms"]) + 1):
            zaal_adres[o.get("note") or o["name"]] = (
                f"plan-{nummer}.html#room-{k}", pl["label"], o.get("note") or o["name"])
    for m in makers.values():
        for naam, adres in zaal_adres.items():
            if in_ruimte(m, naam):
                m["plan_link"] = adres
                break

    for nummer, pl in plannen.items():
        pl = dict(pl, id=str(nummer))
        rooms = []
        for i, naam in enumerate(pl["rooms"], start=1):
            leden = {x["name"] for x in d["echo_members"]}
            overal = [sl for sl, waar in (pl.get("everywhere") or {}).items()
                      if naam in waar]
            vast = pl["rooms"][naam].get("people") or []
            if vast:
                # Een ruimte mag mensen zelf benoemen: als slug, of als naam met
                # een eigen adres. Dat laatste is nodig voor de sprekers op de
                # tweede verdieping; die hebben geen makerspagina maar wel een
                # kaartje op Eventbrite.
                mensen = []
                for x in vast:
                    if isinstance(x, dict):
                        mensen.append({"name": x["name"], "slug": x.get("slug"),
                                       "href": x.get("href")})
                    else:
                        mensen.append({"name": makers[x]["name"], "slug": x,
                                       "kind": makers[x].get("kind")})
            else:
                mensen = [{"name": m["name"], "slug": m["slug"], "kind": m.get("kind")}
                          for m in curated + collectives_ + partners_
                          if (in_ruimte(m, naam) or m["slug"] in overal)
                          and m["name"] not in leden]
            rooms.append({"id": i, "name": naam, "people": mensen})
        for k, o in enumerate(pl.get("outside", []), start=len(pl["rooms"]) + 1):
            rooms.append({"id": k, "name": o.get("note") or o["name"],
                          "people": [{"name": o["name"], "slug": o["slug"]}]})
        # De lijst naast de plattegrond noemt de makers, niet de zalen. Wie een
        # naam zoekt hoeft dan niet eerst te raden in welke zaal die staat.
        # Een maker kan in meer dan een ruimte staan; dan lichten ze allemaal op.
        namen = {}
        for r in rooms:
            for m in r["people"]:
                sleutel = m.get("slug") or m["name"]
                q = namen.setdefault(sleutel, {
                        "name": m["name"], "slug": m.get("slug"),
                        "href": m.get("href") or ((m["slug"] + ".html") if m.get("slug") else None),
                        "page": bool(m.get("href")) or bool(
                            m.get("slug") and not makers.get(m["slug"], {}).get("pending")),
                        "rooms": [], "where": []})
                q["rooms"].append(str(r["id"]))
                q["where"].append(r["name"])
        for m in curated + collectives_ + partners_:
            if m["slug"] in namen or m["name"] in leden:
                continue
            los = (m.get("location") or "")
            overal = (pl.get("everywhere") or {}).get(m["slug"])
            if overal:
                ids = [str(r["id"]) for r in rooms if r["name"] in overal]
                namen[m["slug"]] = {"name": m["name"], "slug": m["slug"],
                                    "href": m["slug"] + ".html",
                                    "page": not m.get("pending"),
                                    "rooms": ids, "where": ["Throughout the rooms"]}
        # Wie wel op de verdieping staat maar van wie de precieze plek nog niet
        # vastligt: in de lijst, zonder ruimte om te laten oplichten. Beter dan
        # iemand in een ruimte zetten waar hij misschien niet staat.
        for sl in (pl.get("elsewhere") or []):
            m = makers.get(sl)
            if not m or sl in namen:
                continue
            namen[sl] = {"name": m["name"], "slug": sl, "href": sl + ".html",
                         "page": not m.get("pending"), "rooms": [],
                         "where": ["Elsewhere on this floor"]}
        plan_people = sorted(namen.values(), key=lambda q: q["name"].split()[-1].lower())
        overal_namen = [makers[sl]["name"] for sl in (pl.get("everywhere") or {})
                        if sl in makers]

        write(f"plan-{nummer}.html", "plan.html", camp=camp,
              page_title=f"Plan of {pl['label'].lower()}",
              page_description=(f"{pl['label']} of {site['venue']['name']}: "
                                "which maker is in which space."),
              og_image=d["building"]["levels"][0].get("hero"),
              plan=pl, plan_rooms=rooms, plan_people=plan_people,
              plan_svg=teken_plan(pl, {r["name"]: r["people"] for r in rooms}),
              plan_overal=overal_namen,
              plan_links=plan_links)

    write("building.html", "building.html", camp=camp,
          page_title="The Metz building, level by level",
          page_description=("Eight levels of " + site["venue"]["name"] + ", the former "
                            "Metz & Co building on the Keizersgracht. What is on each floor, "
                            "who shows there, and the plan of every level."),
          # De plattegronden stonden alleen in het script dat de tekening
          # opbouwt. Een zoekmachine volgt die niet, en /MAP op de bekers wijst
          # juist hierheen. Vandaar een gewone lijst met echte links.
          plattegronden=[{"nr": nr, "href": f"plan-{nr}.html",
                          "naam": next((l.get("kind") for l in d["building"]["levels"]
                                        if str(l["id"]) == str(nr)), None) or f"Level {nr}"}
                         for nr in sorted(plannen)],
          og_image=d["building"]["levels"][3].get("hero"))

    write("makers.html", "makers.html",
          page_title=f"{len(artists)} makers curated at NIO House Amsterdam", makers_shown=artists,
          collectives=collectives_, partners=partners_,
          og_image=next((m["portrait"] for m in curated if m.get("portrait")), None),
          # The count comes from the register, never from a sentence typed by hand.
          # Two earlier versions of this line said "fifteen" while the page said thirty.
          page_description=(f"The {len(artists)} makers curated by MADART Foundation for Season 02 "
                            "GROUND and Maison d'Artiste at NIO House Amsterdam, with full catalogues."),
          maker_groups=[
            # Het lopende seizoen staat bovenaan. Deze groep ontbrak, waardoor
            # de makers van INLINE wel in het register zaten maar nergens op
            # makers.html te zien waren.
            {"label": "Season 03 — INLINE",
             "note": "Six presentations on the fourth floor of NIO House Amsterdam, each "
                     "answering the same question from its own material, medium and visual "
                     "language.",
             "makers": [m for m in artists if "inline" in m["programmes"]]},
            {"label": "Season 02 — GROUND",
             "note": ("Six makers and the ECHO collective hold seven positions on the fourth floor "
                      f"of NIO House Amsterdam. ECHO shows {_in_woorden(len(d['echo_members']))} makers in Gallery 4."),
             "makers": [m for m in artists if "ground" in m["programmes"]]},
            {"label": "Maison d'Artiste — GLUE Amsterdam",
             "note": "Four rooms built for living on the sixth floor, the dome on the seventh, "
                     "the staircases in between, and a running presentation on the second.",
             "makers": [m for m in artists
                        if set(m["programmes"]) & {"maison", "stairwells", "talks"}]},
          ])

    write("works.html", "works.html",
          page_title=f"{len([w for w in work_list if w['image'] and makers.get(w['maker'], {}).get('kind') != 'partner'])} works, the maker\u2019s own price",
          page_description="Every work in the MADART Foundation register, with the maker's own price.",
          works_json=works_json,
          works_with_images=[w for w in work_list if w["image"]
                             and makers.get(w["maker"], {}).get("kind") != "partner"],
          # Het register wordt nu in de bron gezet, in de standaardvolgorde:
          # op maker, dan op titel. Het filter toont en verbergt daarna; het
          # bouwt niets meer op. Zo staan de werken in de HTML voor wie geen
          # JavaScript uitvoert, en dat zijn ook zoekmachines.
          works_rendered=sorted([w for w in work_list if w["image"]
                                 and makers.get(w["maker"], {}).get("kind") != "partner"],
                                key=lambda w: (w["maker_name"].lower(), w["title"].lower())),
          og_image=next((w["image"] for w in featured), None))

    write("exhibitions.html", "exhibitions.html", page_title="Exhibitions",
          og_image="c-exhibition-inline.jpg",
          page_description=("Every season and anchor event at MADART Foundation, documented: what is on "
                            "now at NIO House Amsterdam, what is coming, and what we have shown."),
          exhibition_blocks=[
            {"label": "Current",  "rows": [r for r in rows if r["status"] == "current"]},
            {"label": "Upcoming", "rows": [r for r in rows if r["status"] == "upcoming"]},
            {"label": "Past",     "rows": [r for r in rows if r["status"] == "past"]},
          ])

    write("visit.html", "visit.html",
          page_title="Plan your visit to NIO House Amsterdam", og_image=d["place"]["image"],
          page_description=("Opening hours, directions and the anchor-event programme at NIO House "
                            "Amsterdam, Leidsestraat 32-34. Entry to the gallery floor is free."),
          hours_rows=[{"abbr": a.upper(), "name": n,
                       "hours": (f"{site['hours'][a][0]:02d}:{site['hours'][a][1]:02d} – "
                                 f"{site['hours'][a][2]:02d}:{site['hours'][a][3]:02d}")
                                if site["hours"][a] else "Closed"} for a, n in DAYS])

    md = d["maison"]
    by_slug = {m["slug"]: m for m in maker_list}
    for room in md["rooms"]:
        room["people"] = [by_slug[s] for s in room["makers"] if s in by_slug]
    write(f"{md['slug']}.html", "maison.html", page_title=md["title"],
          event_data={"slug": md["slug"], "name": md["title"], "description": md["standfirst"],
                      "start": "2026-09-17", "end": "2026-09-19",
                      "image": "portrait-marnix-van-strydonck.jpg"},
          page_description=("Maison d'Artiste: an exhibition for GLUE Amsterdam on the sixth and "
                            "seventh floor of NIO House Amsterdam: four rooms built for living, "
                            "furnished by our makers."),
          maison=md,
          og_image="portrait-marnix-van-strydonck.jpg")

    write("404.html", "notfound.html", page_title="Page not found",
          page_description=("This page is not here. If you scanned a code in the gallery, "
                            "email us the title of the work and we will send the right page."))

    write("enquire.html", "enquire.html", page_title="Enquiry",
          page_description=("Ask a maker about a work in the MADART Foundation register. "
                            "The maker sets the price and keeps all of it; we pass the question on "
                            "and take no commission."))
    write("enquiry-thanks.html", "thanks.html", page_title="Enquiry received", noindex=True,
          page_description=("Your question is on its way to the maker. They come back to you "
                            "directly; MADART Foundation takes no part in the sale."),
          thanks={"heading": "Your question is on its way.",
                  "body": "We pass enquiries to the maker the same day. They will come back to you "
                          "directly — MADART Foundation takes no part in the sale and no commission."})

    write("thanks.html", "thanks.html", page_title="Thank you", noindex=True,
          page_description=("You are on the MADART Foundation list. A few times a season we write "
                            "about a new opening, a maker worth knowing about, and nothing else."),
          thanks={"heading": "You are on the list.",
                  "body": "We will write a few times a season — a new season opening, a maker worth "
                          "knowing about, nothing else. You can unsubscribe from any email."})

    if event:
        write("events.html", "event.html", page_title=event["title"],
              event_data={"slug": "events", "name": event["title"],
                          "description": event["standfirst"], "start": str(event["start"]),
                          "end": str(event["end"]), "image": event.get("card")},
              page_description=event["standfirst"], event=event,
              ground_makers=ground, glue_makers=glue)

    OG_STANDALONE = {"privacy": "place-nio-house.jpg",
                     "anbi": "place-nio-house.jpg",
                     }
    for slug, title, desc in [
        ("privacy", "Privacy",
         "What MADART Foundation collects, why, how long we keep it, and what you can ask us to do with it."),
        ("anbi", "Governance and ANBI",
         "Published information on Stichting The Bloys, operating as MADART Foundation: purpose, "
         "policy plan, board, remuneration, selection and finances."),
    ]:
        write(f"{slug}.html", f"{slug}.html", page_title=title, page_description=desc,
              og_image=OG_STANDALONE.get(slug))

    for s in d["seasons"]:
        sm = ground if s["programme"] == "ground" else []
        sdesc = (f"Season {s['number']} — {s['title']} at {s['location']}, {s['dates_label']}. "
                 f"{s['standfirst']}")
        ev = {"slug": s["slug"], "name": f"Season {s['number']} — {s['title']}",
              "description": s["standfirst"], "start": str(s["start"]), "end": str(s["end"]),
              "image": s["hero"] or s.get("card")}
        write(f"{s['slug']}.html", "season.html", event_data=ev,
              page_title=f"Season {s['number']} — {s['title']}",
              page_description=clip(sdesc, 158),
              og_image=s["hero"] or s.get("card"), season=s, season_makers=sm,
              event=event if s["status"] == "current" else None)

    for m in maker_list:
        if m.get("pending"):
            continue
        # Waar de maker toe hoort. Maison d'Artiste en de trappenhuizen vallen
        # niet onder het lopende seizoen; die staan er drie dagen.
        _huidig = next((x for x in d["seasons"] if x["status"] == "current"), None)
        m["season_label"] = ("Maison d'Artiste"
                             if m.get("programme") in ("maison", "stairwells", "talks")
                             else (f"Season {_huidig['number']} — {_huidig['title']}"
                                   if _huidig else ""))
        mw = [works[s] for s in m["works"] if s in works]
        # De ontwerpers van een merk: codes omzetten naar werken, en een
        # portret alleen tonen als het bestaat. Een ontbrekend beeld mag het
        # blok niet breken — de tekst is op zichzelf al waardevol.
        for _dz in (m.get("designers") or []):
            _dz["works"] = [works[s_] for s_ in works
                            if works[s_].get("code") in (_dz.get("codes") or [])]
            if _dz.get("portrait") and not (ASSETS / _dz["portrait"]).exists():
                _dz["portrait"] = None

        # Een externe maker staat volledig in het register — makers.html,
        # works.html, de sitemap, de plattegrond en de carrousel — maar zijn
        # pagina wordt elders gebouwd. Die hier schrijven zou hem overschrijven.
        if m.get("extern"):
            continue
        write(f"{m['slug']}.html", "maker.html", page_title=m["name"],
              page_description=maker_meta(m, len(mw),
                  "17 to 19 September 2026" if m.get("programme") in ("maison", "talks")
                  else "until 30 September 2026"),
              maker=m, maker_works=mw,
              members=([makers[s] for s in (m.get("members") or []) if s in makers]
                       if m.get("category") == "collective" else None),
              # Curated makers and collectives only. Brand partners have their own
              # rail on the home page; mixing them in here would blur the line
              # between who is curated and who is presented alongside.
              nearby=[x for x in maker_list
                      if x["slug"] != m["slug"] and x.get("portrait")
                      and not x.get("pending") and x.get("category") == "artist"],
              all_makers_count=len(artists),
              og_image=(mw[0]["image"] if mw else None))

    seen_titles = collections.Counter()
    for w in work_list:
        s = next((x for x in d["seasons"] if x["status"] == "current"), None)
        # Where the work actually hangs. Both exhibitions run at the same time, so
        # the current season is not the answer for a work in Maison d'Artiste — and
        # the stairwells belong to Maison d'Artiste too, not to GROUND.
        in_maison = w["programme"] in ("maison", "stairwells")
        where = (f"Maison d'Artiste" if in_maison
                 else f"Season {s['number']} — {s['title']}")

        # Three works are called M15. A title that repeats is a title that ranks
        # for nothing, so the material disambiguates it.
        # Google truncates long titles in the result, but a title that is not unique
        # ranks for nothing at all. Uniqueness wins; the title stays whole.
        same = [x for x in work_list if x["title"] == w["title"] and x["maker"] == w["maker"]]
        label = w["title"]
        if len(same) > 1 and w["materials"]:
            parts = [p.strip() for p in w["materials"].split("·")]
            material, dims = parts[0], (parts[1] if len(parts) > 1 else "")
            twins = [x for x in same if x["materials"]
                     and x["materials"].split("·")[0].strip() == material]
            label = f"{w['title']}, {dims or material}"
        title = f"{label} — {w['maker_name']}"
        # The template appends " — MADART FOUNDATION" (20 chars). When the work's
        # own name already fills the line, drop the suffix rather than truncate
        # the title: a cut-off name helps nobody, a missing brand costs nothing.
        w["short_suffix"] = len(title) > 42

        price = w["price_label"] if w["price_eur"] else "Price on request"
        # Built from whole sentences in order of importance, never cut to length.
        # A hard slice at 158 left thirty-four snippets ending on "keeps all of i",
        # and it swallowed the exhibition on the works with the longest materials
        # line. Materials is the first thing to go when the budget runs out.
        core = [f"{w['title']} by {w['maker_name']}.",
                f"{price}, and the maker keeps all of it.",
                f"On view in {where} at NIO House Amsterdam."]
        full = list(core)
        if w["materials"]:
            full.insert(1, f"{re.sub(r'[.\s]+$', '', w['materials'])}.")
        desc = re.sub(r"\s+", " ", " ".join(full))
        if len(desc) > 158:
            desc = re.sub(r"\s+", " ", " ".join(core))

        if w.get("extern"):
            continue
        write(f"{w['slug']}.html", "work.html", page_title=title, page_description=desc,
              work=w, og_image=w["image"], season=s,
              maker=makers.get(w["maker"]))

    write("support-us.html", "support.html", page_title="Support us",
          og_image="place-nio-house.jpg",
          page_description=("Support MADART Foundation: give once, give every year, or become a "
                            "Friend. Every artwork sale goes to the maker; gifts pay for the room."),
          giving=d["giving"])
    write("friend.html", "friend.html", page_title="Friend of MADART Foundation",
          og_image="place-nio-house.jpg",
          page_description=("Friend of MADART Foundation is a yearly gift, not a ticket: the season "
                            "letter, the curatorial notes, and where the gifts went."),
          friend=d["friend"], giving=d["giving"])

    for slug, p in d["pages"].items():
        if slug == "support-us":
            continue
        slug = RENAMED.get(slug + ".html", slug + ".html")[:-5]
        # Een tekstpagina mag een eigen titel dragen; het label is voor de
        # navigatie, niet voor het zoekresultaat.
        write(f"{slug}.html", "page.html", page_title=(p.get("title") or p["label"]),
              page_description=(p.get("meta") or clip(p.get("lede") or "")),
              og_image=p.get("og_image"), page=p)

    # ---- de twee vaste adressen op de bekers -------------------------
    # Tienduizend bekers dragen jarenlang hetzelfde adres. MAP en PROG wijzigen
    # daarom nooit van naam; ze verwijzen door naar de echte pagina's, en dat
    # doel verschuift per seizoen. Geen tweede plattegrond, geen tweede
    # programma: een kopie loopt vroeg of laat uit de pas met het origineel.
    if camp:
        if not camp.get("endpoint_foundation"):
            print("  LET OP  het aanmeldscherm op de bekerroute heeft nog geen "
                  "formulieradres — het verzamelt niets")
        for kort, doel in (("MAP.html", camp["map_target"]),
                           ("PROG.html", camp["prog_target"])):
            OUT.joinpath(kort).write_text(
                env.get_template("cup-redirect.html").render(
                    site=site, target=doel, merk=camp.get("batch") or "1"),
                encoding="utf-8")

    # static + assets pass straight through
    shutil.copy(STATIC/"style.css", OUT/"style.css")
    if ASSETS.exists():
        for a in ASSETS.iterdir():
            if a.is_file():
                shutil.copy(a, OUT/a.name)
    # Wat onaf is hoort in de console te staan, niet op de pagina.
    giving = d.get("giving", {})
    if not [x for x in giving.get("amounts", []) if x.get("link")]:
        print("  LET OP  geen betaallinks onder giving.amounts —"
              " de doneerpagina toont alleen de bankgegevens")
    if "[" in str(giving.get("bank", {}).get("iban", "")):
        print("  LET OP  het IBAN is nog een placeholder en staat zo op de pagina")
    if "1DWonyUTP" in str(site.get("newsletter_endpoint", "")):
        print("  LET OP  het formulieradres begint met een cijfer een; in Formspark"
              " staat een kleine letter L. Zo komt er niets aan.")

    (OUT/"CNAME").write_text("madartfoundation.com\n")
    (OUT/"robots.txt").write_text(
        "User-agent: *\nAllow: /\n\nSitemap: https://madartfoundation.com/sitemap.xml\n")

    # Dutch file names on an English site. The English name becomes the real page;
    # the old name stays behind as a redirect, because links and search results
    # pointing at it must not break.
    for old, new in RENAMED.items():
        html = env.get_template("redirect.html").render(site=site, target=new)
        (OUT/old).write_text(html, encoding="utf-8")

    # Externe pagina's staan niet in OUT — ze worden elders gebouwd — maar ze
    # bestaan wel op de site en horen dus in de sitemap.
    extern_urls = sorted({f"{x['slug']}.html" for x in makers.values()
                          if isinstance(x, dict) and x.get("extern")}
                         | {f"{x['slug']}.html" for x in works.values()
                            if isinstance(x, dict) and x.get("extern")})
    urls = sorted(set(p.name for p in OUT.glob("*.html")) | set(extern_urls))
    sm = ['<?xml version="1.0" encoding="UTF-8"?>',
          '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        # Bevestigingspagina's hebben niets te vinden. En een pagina met
        # noindex hoort niet in de sitemap: die twee spreken elkaar tegen, en
        # dat is precies wat een zoekmachine als fout meldt.
        # MAP en PROG zijn kortere versies van building.html en de
        # programmapagina, bedoeld voor wie een beker vasthoudt. Ze horen niet
        # in de index: twee pagina's over hetzelfde onderwerp concurreren met
        # elkaar, en de uitgebreide versie moet winnen.
        buiten = {"404.html", "thanks.html", "enquiry-thanks.html",
                  "MAP.html", "PROG.html"}
        if u in RENAMED or u in buiten:
            continue
        loc = site["url"] + "/" + ("" if u == "index.html" else u)
        prio = "1.0" if u == "index.html" else ("0.9" if u in
               ("works.html","exhibitions.html","makers.html","visit.html") else "0.7")
        sm += ["  <url>", f"    <loc>{loc}</loc>",
               f"    <lastmod>{TODAY}</lastmod>",
               f"    <priority>{prio}</priority>", "  </url>"]
    sm.append("</urlset>")
    (OUT/"sitemap.xml").write_text("\n".join(sm) + "\n")

    return urls


def check(urls):
    """No URL that ever existed may disappear. QR codes depend on it."""
    if not LOCK.exists():
        LOCK.write_text("\n".join(urls) + "\n")
        print(f"urls.lock created with {len(urls)} URLs")
        return 0
    known = [u for u in LOCK.read_text().split() if u]
    missing = sorted(set(known) - set(urls))
    added = sorted(set(urls) - set(known))
    if missing:
        print("BUILD REJECTED — these URLs would disappear:")
        for u in missing:
            print("   ", u)
        return 1
    if added:
        LOCK.write_text("\n".join(sorted(set(known) | set(urls))) + "\n")
        print(f"{len(added)} new URLs added to urls.lock")
    print(f"URL check passed — {len(urls)} pages, none lost")
    return 0


if __name__ == "__main__":
    urls = build()
    print(f"built {len(urls)} pages into {OUT}")
