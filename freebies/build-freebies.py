#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VanKompass Freebie-Generator.
Liest freebies-data.json und erzeugt 16 druckfertige Freebie-HTML-Dateien
(identische CI via freebie-styles.css) plus eine index.html-Uebersicht.
Mit --pdf werden zusaetzlich PDFs ueber Google Chrome (headless) gerendert.

Aufruf:
  python3 build-freebies.py          # nur HTML + index
  python3 build-freebies.py --pdf    # zusaetzlich PDFs nach ./pdf/
"""
import json, os, sys, html, subprocess, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "freebies-data.json")

SILO_NAME = {
    "cockpit": "Cockpit", "strom": "Batterie & Strom", "solar": "Solar",
    "schlafen": "Schlafen", "sanitaer": "Toilette & Sanitär", "kueche": "Küche",
    "wasser": "Wasser", "heizung": "Heizung", "verdunkelung": "Verdunkelung & Insektenschutz",
    "stauraum": "Stauraum", "aussenbereich": "Außenbereich", "sicherheit": "Sicherheit",
    "internet": "Internet", "apps": "Camper-Apps", "sitze": "Sitze & Drehkonsole", "sound": "Sound",
}
TYPE_LABEL = {
    "checkliste": "Checkliste", "rechen-worksheet": "Rechen-Vorlage",
    "entscheidungshilfe": "Entscheidungshilfe", "kuratierte-uebersicht": "Übersicht",
    "mini-guide": "Kurz-Guide",
}
CHECK_TYPES = {"checkliste", "rechen-worksheet"}


def esc(s):
    return html.escape(s or "", quote=True)


def render_freebie(fb):
    silo = fb["siloSlug"]
    kind = TYPE_LABEL.get(fb.get("freebieType", ""), "Freebie")
    items_cls = "check" if fb.get("freebieType") in CHECK_TYPES else "arrow"

    blocks_html = []
    for b in fb.get("contentBlocks", []):
        parts = ['<section class="block">']
        parts.append("<h2>%s</h2>" % esc(b.get("heading", "")))
        if b.get("body"):
            parts.append("<p>%s</p>" % esc(b["body"]))
        items = b.get("items") or []
        if items:
            lis = "".join("<li>%s</li>" % esc(it) for it in items)
            parts.append('<ul class="items %s">%s</ul>' % (items_cls, lis))
        parts.append("</section>")
        blocks_html.append("\n".join(parts))

    doc = f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>{esc(fb.get('freebieTitle',''))} | VanKompass</title>
<link rel="stylesheet" href="freebie-styles.css">
</head>
<body>
<div class="doc">
  <header class="cover">
    <div class="brand"><span class="mark">V</span> VanKompass</div>
    <div class="kind">{esc(kind)} &middot; {esc(SILO_NAME.get(silo, silo))}</div>
  </header>
  <div class="body">
    <h1>{esc(fb.get('freebieTitle',''))}</h1>
    <p class="hook">{esc(fb.get('coverHook',''))}</p>
    <div class="why"><strong>Warum das hilft:</strong> {esc(fb.get('whyUseful',''))}</div>
    {chr(10).join(blocks_html)}
    <div class="cta"><strong>Wie es weitergeht</strong>{esc(fb.get('softCta',''))}</div>
  </div>
  <div class="foot">
    <span class="bk">VanKompass</span> &middot; {esc(fb.get('freebieTitle',''))} &middot; Stand Juni 2026 &middot;
    ENTWURF, Beispieldaten, vor Live verifizieren. Dieser Ratgeber kann Werbe-/Affiliate-Hinweise enthalten.
    Bei sicherheitsrelevanten Einbauten (Strom, Gas, Heizung) im Zweifel eine Fachwerkstatt einbeziehen.
  </div>
</div>
</body>
</html>
"""
    return doc


def render_index(freebies):
    cards = []
    for fb in freebies:
        silo = fb["siloSlug"]
        cards.append(f"""<div class="idx-card">
  <div class="silo">{esc(SILO_NAME.get(silo, silo))} &middot; {esc(TYPE_LABEL.get(fb.get('freebieType',''),''))}</div>
  <h3>{esc(fb.get('freebieTitle',''))}</h3>
  <a href="freebie-{esc(silo)}.html">Ansehen</a> &nbsp; <a href="pdf/freebie-{esc(silo)}.pdf">PDF</a>
</div>""")
    return f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>VanKompass Freebies (16 Bereiche)</title>
<link rel="stylesheet" href="freebie-styles.css">
</head>
<body style="background:#f4ead7;">
<div class="idx-hero">
  <div class="idx-wrap" style="padding-bottom:0;">
    <h1>VanKompass Freebies</h1>
    <p>Ein Freebie pro Bereich (Silo). Innerhalb eines Bereichs ist es fuer alle Artikel identisch. Alle in einer CI, ueber Brevo als Lead-Magnet auslieferbar.</p>
  </div>
</div>
<div class="idx-wrap">
  <div class="idx-note"><strong>16 Freebies, 16 Bereiche.</strong> Modell-Hubs (z.B. VW California) tragen bewusst kein Freebie. Stand: Entwurf, Juni 2026.</div>
  <div class="idx-grid">
    {chr(10).join(cards)}
  </div>
</div>
</body>
</html>
"""


def make_pdfs(freebies):
    chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    if not os.path.exists(chrome):
        print("Chrome nicht gefunden, ueberspringe PDF.")
        return 0
    pdfdir = os.path.join(HERE, "pdf")
    os.makedirs(pdfdir, exist_ok=True)
    n = 0
    for fb in freebies:
        silo = fb["siloSlug"]
        src = os.path.join(HERE, f"freebie-{silo}.html")
        out = os.path.join(pdfdir, f"freebie-{silo}.pdf")
        url = "file://" + urllib.request.pathname2url(src)
        try:
            subprocess.run([chrome, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                            f"--print-to-pdf={out}", url],
                           check=True, capture_output=True, timeout=60)
            n += 1
        except Exception as e:
            print(f"PDF-Fehler {silo}: {e}")
    return n


def main():
    with open(DATA, encoding="utf-8") as f:
        freebies = json.load(f)
    for fb in freebies:
        path = os.path.join(HERE, f"freebie-{fb['siloSlug']}.html")
        with open(path, "w", encoding="utf-8") as out:
            out.write(render_freebie(fb))
    with open(os.path.join(HERE, "uebersicht.html"), "w", encoding="utf-8") as out:
        out.write(render_index(freebies))
    print(f"{len(freebies)} Freebie-HTML + index.html erzeugt.")
    if "--pdf" in sys.argv:
        n = make_pdfs(freebies)
        print(f"{n} PDFs gerendert nach ./pdf/")


if __name__ == "__main__":
    main()
