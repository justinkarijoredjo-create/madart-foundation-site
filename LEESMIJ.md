# Upload 9 september 2026 — vier bestanden

Gebouwd op de broncode zoals die op 9 september in
`justinkarijoredjo-create/madart-foundation-site` (main) stond.
Geen enkele wijziging raakt `style.css` — dus geen herupload van 232 pagina's.

## Uploadvolgorde

### Ronde 1 — twee bestanden, geen risico

**`index.html`**
Kopstructuur gewijzigd. Visueel verandert er niets.
- `<h1 class="display">GROUND</h1>` → `<h2 class="display">GROUND</h2>`
- `<h2 class="claim">We curate the makers…</h2>` → `<h1 class="claim">…</h1>`

Waarom identiek in beeld: `.display` en `.claim` zetten font-size, line-height,
letter-spacing, font-weight en margin zelf. Een klasse wint van een elementregel,
dus de generieke `h1{}` en `h2{}` uit `style.css` komen er niet doorheen.
Gecontroleerd: geen enkel script selecteert op `h1`.

Bestandsgrootte ongewijzigd. Aantal koppen: 1× h1, 8× h2.

**`maison-dartiste-2026.html`**
Eén tekenreeks hersteld: `&amp;rsquo;` → `&#39;`.
Stond zichtbaar op de pagina in het kadertje onder Opening Night
("the Foundation&rsquo;s own exhibition"). Verschil: 6 bytes.

### Ronde 2 — twee bestanden, apart uploaden en direct testen

**`MAP.html`** en **`PROG.html`**

> **Let op de bestandsnaam.** Beide in HOOFDLETTERS. GitHub is
> hoofdlettergevoelig; `map.html` maakt een tweede bestand aan en laat
> elk van de 10.000 bekers op een 404 uitkomen.

Toegevoegd aan de doorverwijzing:
`&utm_source=beker&utm_medium=qr&utm_campaign=glue26&utm_content=map` (resp. `prog`)

Gecontroleerd vóór de bouw: het aanmeldscherm leest de parameter op naam
(`new URLSearchParams(location.search).get("c")`), dus extra parameters
breken het niet. Na parsing: `c=1`, `utm_source=beker`, `utm_content=map`.
In de HTML-attributen staat elke ampersand als `&amp;`, in de JavaScript-regel
als gewone `&` — dat hoort zo.

## Testen na upload

1. `madartfoundation.com/MAP` op je telefoon → moet op `building.html` uitkomen
   met het aanmeldscherm, en het adres eindigt op `utm_content=map`.
2. `madartfoundation.com/PROG` → hetzelfde, op de programmapagina.
3. Simple Analytics → Referrals: er verschijnt binnen enkele minuten
   een regel **beker**.

Werkt stap 1 niet: controleer eerst of het bestand `MAP.html` heet en niet
`map.html`. Dat is de enige realistische foutbron.

## Wat hierna nog in de generator moet

Deze vier bestanden zijn rechtstreeks bewerkt. Bij de eerstvolgende volledige
herbouw worden ze overschreven, tenzij de bron meegaat:

- Kopstructuur: in het sjabloon van de homepage.
- `&rsquo;`: in `data/programme.yaml`. Vervang de HTML-entiteit door een
  gewone apostrof; het sjabloon escapet zelf al.
- UTM: in het sjabloon of het script dat `MAP.html` en `PROG.html` genereert.
