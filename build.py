#!/usr/bin/env python3
"""Erzeugt alle Portalseiten (Magazin, Bereiche, Camper + 16 Bereichs- und 7 Camper-Portale)
aus data/fragments/*.json. Aufruf: python3 build.py"""
import datetime
import glob
import json
import os
import sys
from xml.sax.saxutils import escape

from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

SITE = {
    "base": "https://vankompass.de/",
    "css_v": "5",
    "top_bereich": "strom",
    "top_beitrag": "aferiy-p180-pro-ford-nugget",
    "indexnow_key": "757ee0c8954ba62d7df91e7af93af9ea",
    "asset_v": "20261011",
    "kontakt": "redaktion@vankompass.de",
    "affiliate_hinweis": "Einige Links auf dieser Seite sind Affiliate-Links. Kaufst du darüber ein, erhalten wir eine kleine Provision. Für dich ändert sich am Preis nichts. So können wir VanKompass betreiben und die Inhalte, Checklisten und Packlisten weiterhin kostenlos anbieten. Danke für deine Unterstützung.",
    "freebie": {
        "titel": "Die VanKompass Camper-Packliste: 120 Punkte, nach Bereichen sortiert",
        "text": "Strom, Schlafen, Küche, Sanitär, Sicherheit, Werkzeug. Zum Abhaken vor jeder Fahrt, damit du nie wieder ohne Ladekabel, Wasserschlauch oder Keil losfährst.",
        "benefits": [
            "Alle Bereiche auf einen Blick, auch die, an die niemand denkt",
            "Extra-Spalte für dein eigenes Camper-Modell",
            "Neue Video-Tests und Ratgeber direkt ins Postfach",
        ],
        "titel_kurz": "Die Camper-Packliste als PDF, kostenlos",
        "text_kurz": "120 Punkte nach Bereichen sortiert. Dazu neue Video-Tests und Ratgeber, sobald sie online sind.",
        "button": "Packliste holen",
    },
}

BEREICH_ORDER = ["strom", "solar", "schlafen", "sanitaer", "kueche", "wasser", "heizung", "verdunkelung",
                 "cockpit", "stauraum", "aussenbereich", "sicherheit", "internet", "camper-apps", "sitze", "sound"]
CAMPER_ORDER = ["vw-california", "vw-grand-california", "ford-nugget", "marco-polo", "poessl-ducato", "knaus", "sprinter-ausbau"]

ICONS = {
    "strom": '<path d="M13 2L4 14h6l-1 8 9-12h-6l1-8z"/>',
    "solar": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M4.9 19.1l1.4-1.4M17.7 6.3l1.4-1.4"/>',
    "schlafen": '<path d="M2 20v-9a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v9M2 16h20M6 9V7a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v2"/>',
    "sanitaer": '<path d="M12 3s6 6.5 6 11a6 6 0 0 1-12 0c0-4.5 6-11 6-11z"/>',
    "kueche": '<path d="M4 10h16v7a3 3 0 0 1-3 3H7a3 3 0 0 1-3-3v-7zM2 10h20M9 7V5M12 7V4M15 7V5"/>',
    "wasser": '<path d="M3 8c2-2 4-2 6 0s4 2 6 0 4-2 6 0M3 14c2-2 4-2 6 0s4 2 6 0 4-2 6 0M3 20c2-2 4-2 6 0s4 2 6 0 4-2 6 0"/>',
    "heizung": '<path d="M12 3c1.2 3.2 4.5 5.4 4.5 9.3A4.5 4.5 0 0 1 7.5 12.3c0-1.6.6-2.9 1.5-4 .3 1.4 1 2.3 1.9 2.8C11.6 9.2 11 6 12 3z"/>',
    "verdunkelung": '<path d="M21 13A9 9 0 1 1 11 3a7 7 0 0 0 10 10z"/>',
    "cockpit": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="3"/><path d="M3.3 10.5h5.9M14.8 10.5h5.9M12 15v6"/>',
    "stauraum": '<path d="M3 8l9-5 9 5v9l-9 5-9-5V8zM3 8l9 5 9-5M12 13v9"/>',
    "aussenbereich": '<path d="M2 20L12 4l10 16H2zM12 20v-8"/>',
    "sicherheit": '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6l8-3z"/>',
    "internet": '<path d="M2 9a15 15 0 0 1 20 0M5.5 12.5a10 10 0 0 1 13 0M9 16a5 5 0 0 1 6 0"/><circle cx="12" cy="19.5" r="1"/>',
    "camper-apps": '<rect x="7" y="2" width="10" height="20" rx="2"/><path d="M11 18h2"/>',
    "sitze": '<path d="M7 3h8l-1 10H8L7 3zM5 13h14l1 7H4l1-7zM8 20v2M16 20v2"/>',
    "sound": '<rect x="5" y="2" width="14" height="20" rx="2"/><circle cx="12" cy="14" r="4"/><circle cx="12" cy="7" r="1.5"/>',
    "camper": '<path d="M3 16V9a2 2 0 0 1 2-2h8l5 4h1a2 2 0 0 1 2 2v3M3 16h18"/><circle cx="7" cy="17" r="2"/><circle cx="17" cy="17" r="2"/>',
    "plus": '<path d="M12 5v14M5 12h14"/>',
}

FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif"


def write(path, content):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def thumb_svg(l1, l2, tag):
    l1, l2, tag = escape(l1), escape(l2), escape(tag.upper())
    return f'''<svg width="680" height="400" viewBox="0 0 680 400" xmlns="http://www.w3.org/2000/svg" role="img">
<title>{l1} {l2}</title>
<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0f3d3e"/><stop offset="1" stop-color="#14504f"/></linearGradient></defs>
<rect width="680" height="400" rx="14" fill="url(#bg)"/>
<rect x="30" y="30" width="620" height="340" rx="10" fill="none" stroke="#1f5e5d" stroke-width="1"/>
<text x="60" y="90" font-family="{FONT}" font-size="12" font-weight="600" letter-spacing="3" fill="#e08a2b">VANKOMPASS MAGAZIN</text>
<rect x="60" y="102" width="56" height="3" rx="1.5" fill="#e08a2b"/>
<text x="60" y="190" font-family="{FONT}" font-size="38" font-weight="700" fill="#ffffff" letter-spacing="-0.8">{l1}</text>
<text x="60" y="238" font-family="{FONT}" font-size="38" font-weight="700" fill="#ffffff" letter-spacing="-0.8">{l2}</text>
<rect x="60" y="300" width="{len(tag) * 9 + 32}" height="32" rx="16" fill="#e08a2b"/>
<text x="76" y="321" font-family="{FONT}" font-size="13" font-weight="700" fill="#0f3d3e" letter-spacing="0.5">{tag}</text>
<text x="620" y="352" text-anchor="end" font-family="{FONT}" font-size="11" fill="#5d7b76">vankompass.de</text>
</svg>
'''


def product_svg(name):
    name = escape(name)
    return f'''<svg width="520" height="520" viewBox="0 0 520 520" xmlns="http://www.w3.org/2000/svg" role="img">
<title>{name} (Platzhalter)</title>
<defs><radialGradient id="g" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#e08a2b" stop-opacity="0.3"/><stop offset="1" stop-color="#e08a2b" stop-opacity="0"/></radialGradient></defs>
<circle cx="260" cy="280" r="220" fill="url(#g)"/>
<rect x="110" y="140" width="300" height="260" rx="28" fill="#1b2423" stroke="#3a4645" stroke-width="2"/>
<rect x="126" y="156" width="268" height="18" rx="7" fill="#e08a2b"/>
<text x="260" y="290" text-anchor="middle" font-family="{FONT}" font-size="22" font-weight="700" fill="#ffffff">{name}</text>
<text x="260" y="320" text-anchor="middle" font-family="{FONT}" font-size="12" letter-spacing="2" fill="#8aaba6">PRODUKTFOTO FOLGT</text>
<ellipse cx="260" cy="430" rx="150" ry="14" fill="#000" opacity="0.15"/>
</svg>
'''


def load_fragments():
    bereiche, camper = {}, {}
    for path in sorted(glob.glob("data/fragments/*.json")):
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        (bereiche if d["typ"] == "bereich" else camper)[d["slug"]] = d
    missing_b = [s for s in BEREICH_ORDER if s not in bereiche]
    missing_c = [s for s in CAMPER_ORDER if s not in camper]
    if missing_b or missing_c:
        print("FEHLT:", missing_b, missing_c, file=sys.stderr)
    return [bereiche[s] for s in BEREICH_ORDER if s in bereiche], [camper[s] for s in CAMPER_ORDER if s in camper]


def enrich(bereiche, camper):
    bname = {b["slug"]: b["name"] for b in bereiche}
    for b in bereiche:
        b["out"] = f"{b['slug']}.html"
        for p in b["beitraege"]:
            p["bereich"] = b["slug"]
            p["bereich_name"] = b["name"]
    for c in camper:
        c["out"] = f"camper-{c['slug']}.html"
        for p in c["beitraege"]:
            p.setdefault("bereich", "")
            p["bereich_name"] = bname.get(p["bereich"], "")
            p.setdefault("camper", [c["slug"]])
    for d in bereiche + camper:
        e = d["empfehlung"]
        if not e.get("img"):
            e["img"] = f"img/produkt-{d['slug']}.svg"
        if not os.path.exists(e["img"]):
            write(e["img"], product_svg(e["name"]))
        for p in d["beitraege"]:
            if p.get("status") != "live":
                p["status"] = "geplant"
                p["thumb"] = f"img/thumb-{p['slug']}.svg"
                if not os.path.exists(p["thumb"]):
                    write(p["thumb"], thumb_svg(p.get("thumb_l1", ""), p.get("thumb_l2", ""), p.get("kategorie", "Ratgeber")))


def sort_posts(posts):
    live = sorted([p for p in posts if p["status"] == "live"], key=lambda p: p.get("datum", ""), reverse=True)
    return live + [p for p in posts if p["status"] != "live"]


def flagship_of(posts):
    s = sort_posts(posts)
    top = [p for p in s if p.get("top") and p["status"] == "live"]
    return (top or s or [None])[0]


def load_beitraege():
    out = []
    for path in sorted(glob.glob("data/beitraege/*.json")):
        with open(path, encoding="utf-8") as f:
            a = json.load(f)
        a["status"] = "live"
        a["url"] = a["out"]
        a.setdefault("quelle", "Video von " + a["video"]["kanal"])
        a.setdefault("extra", a["video"]["dauer_text"] + " Video")
        out.append(a)
    return out


def merge_beitraege(beitraege, bereiche):
    by_slug = {b["slug"]: b for b in bereiche}
    for a in beitraege:
        b = by_slug[a["bereich"]]
        a["bereich_name"] = b["name"]
        b["beitraege"] = [a] + [p for p in b["beitraege"] if p["slug"] != a["slug"]]


def jsonld(graph):
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=2).replace("</", "<\\/")


def crumbs_ld(crumbs):
    return {"@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": c["name"], "item": SITE["base"] + c["url"]} for i, c in enumerate(crumbs)]}


def faq_ld(items):
    return {"@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": f["q"], "acceptedAnswer": {"@type": "Answer", "text": " ".join(f["a"])}} for f in items]}


def list_ld(posts):
    return {"@type": "ItemList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": p["title"], **({"url": SITE["base"] + p["url"]} if p["status"] == "live" else {})}
        for i, p in enumerate(posts)]}


def main():
    env = Environment(loader=FileSystemLoader("templates"), autoescape=select_autoescape(["html"]), trim_blocks=True, lstrip_blocks=True)
    env.globals.update(site=SITE, icons=ICONS)
    bereiche, camper = load_fragments()
    enrich(bereiche, camper)
    beitraege = load_beitraege()
    merge_beitraege(beitraege, bereiche)

    all_area_posts = [p for b in bereiche for p in b["beitraege"]]
    env.globals["top"] = next(b for b in bereiche if b["slug"] == SITE["top_bereich"])["empfehlung"]
    for b in bereiche:
        b["flagship"] = flagship_of(b["beitraege"])
    for c in camper:
        tagged = [p for p in all_area_posts if c["slug"] in p.get("camper", [])]
        seen, merged = set(), []
        for p in sort_posts(c["beitraege"] + tagged):
            if p["slug"] not in seen:
                seen.add(p["slug"]); merged.append(p)
        c["posts"] = merged
        c["flagship"] = flagship_of(merged)

    written = []

    def render(tpl, out, **ctx):
        html = env.get_template(tpl).render(out=out, **ctx)
        write(out, html)
        written.append(out)

    # Bereichs-Portale
    for i, b in enumerate(bereiche):
        posts = sort_posts(b["beitraege"])[:6]
        related = [x for x in bereiche if x is not b][:6]
        crumbs = [{"name": "Start", "url": ""}, {"name": "Bereiche", "url": "bereiche.html"}, {"name": b["name"], "url": b["out"]}]
        graph = [crumbs_ld(crumbs),
                 {"@type": "CollectionPage", "@id": SITE["base"] + b["out"], "name": b["meta_title"], "description": b["meta_desc"],
                  "url": SITE["base"] + b["out"], "isPartOf": {"@id": SITE["base"] + "#site"}, "mainEntity": list_ld(posts)},
                 faq_ld(b["faq"])]
        render("portal.html", b["out"], d=b, nav="bereiche", crumbs=crumbs, flagship=b["flagship"], posts=posts, related=related,
               meta_title=b["meta_title"], meta_desc=b["meta_desc"], og_image=b["flagship"]["thumb"], jsonld=jsonld(graph))

    # Camper-Portale
    for c in camper:
        posts = c["posts"][:6]
        related = [x for x in camper if x is not c][:6]
        crumbs = [{"name": "Start", "url": ""}, {"name": "Camper", "url": "camper.html"}, {"name": c["name"], "url": c["out"]}]
        graph = [crumbs_ld(crumbs),
                 {"@type": "CollectionPage", "@id": SITE["base"] + c["out"], "name": c["meta_title"], "description": c["meta_desc"],
                  "url": SITE["base"] + c["out"], "isPartOf": {"@id": SITE["base"] + "#site"}, "mainEntity": list_ld(posts)},
                 faq_ld(c["faq"])]
        render("portal.html", c["out"], d=c, nav="camper", crumbs=crumbs, flagship=c["flagship"], posts=posts, related=related,
               meta_title=c["meta_title"], meta_desc=c["meta_desc"], og_image=c["flagship"]["thumb"], jsonld=jsonld(graph))

    # Magazin-Hub: alle Live-Beitraege + je Bereich ohne Live-Beitrag dessen erster geplanter
    mag_posts = sort_posts([p for p in all_area_posts if p["status"] == "live"]
                           + [b["flagship"] for b in bereiche if b["flagship"] and b["flagship"]["status"] != "live"])
    counts = {}
    for p in mag_posts:
        counts[p["bereich"]] = counts.get(p["bereich"], 0) + 1
    top_post = next((p for p in mag_posts if p["slug"] == SITE["top_beitrag"]), mag_posts[0])
    bmp = [{"slug": b["slug"], "name": b["kurzname"], "count": counts[b["slug"]]} for b in bereiche if b["slug"] in counts]
    crumbs = [{"name": "Start", "url": ""}, {"name": "Magazin", "url": "magazin.html"}]
    graph = [crumbs_ld(crumbs), {"@type": "CollectionPage", "@id": SITE["base"] + "magazin.html", "name": "VanKompass Magazin",
             "description": "Video-Tests, Ratgeber und Praxisberichte aus allen Bereichen rund um Camper und Vanlife.",
             "url": SITE["base"] + "magazin.html", "isPartOf": {"@id": SITE["base"] + "#site"}, "mainEntity": list_ld(mag_posts)}]
    render("magazin.html", "magazin.html", nav="magazin", crumbs=crumbs, flagship=top_post, posts=mag_posts, bereiche=bereiche,
           bereiche_mit_posts=bmp, meta_title="VanKompass Magazin: Camper-Wissen aus Video-Tests und Ratgebern",
           meta_desc="Video-Tests, Ratgeber und Praxisberichte aus allen Bereichen rund um Camper und Vanlife: Strom, Schlafen, Küche, Sanitär, Heizung und mehr. Neutral zusammengefasst mit allen Fakten.",
           og_image=top_post["thumb"], jsonld=jsonld(graph))

    # Startseite
    crumbs = [{"name": "Start", "url": ""}]
    graph = [
        {"@type": "Organization", "@id": SITE["base"] + "#org", "name": "VanKompass", "url": SITE["base"],
         "description": "Redaktionelle Kaufberatung für Camper-Ausrüstung nach Bereich und Modell."},
        {"@type": "WebSite", "@id": SITE["base"] + "#site", "url": SITE["base"], "name": "VanKompass", "publisher": {"@id": SITE["base"] + "#org"}},
        crumbs_ld(crumbs),
        {"@type": "ItemList", "name": "Camper-Ausrüstung nach Bereich", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": b["name"], "url": SITE["base"] + b["out"]} for i, b in enumerate(bereiche)]},
    ]
    render("index.html", "index.html", nav="", crumbs=crumbs, flagship=top_post, posts=mag_posts[:6], bereiche=bereiche, camper=camper,
           meta_title="VanKompass: Camper-Ausrüstung nach Bereich und nach deinem Modell",
           meta_desc="Camper-Ausrüstung nach Bereich und nach deinem Camper-Modell. Video-Tests, Ratgeber und klare Empfehlungen: Strom, Schlafen, Küche, Sanitär, Heizung und mehr.",
           og_image=top_post["thumb"], jsonld=jsonld(graph))

    # Bereiche-Hub
    crumbs = [{"name": "Start", "url": ""}, {"name": "Bereiche", "url": "bereiche.html"}]
    graph = [crumbs_ld(crumbs), {"@type": "CollectionPage", "@id": SITE["base"] + "bereiche.html", "name": "Camper-Ausrüstung nach Bereich",
             "url": SITE["base"] + "bereiche.html", "isPartOf": {"@id": SITE["base"] + "#site"},
             "mainEntity": {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": b["name"], "url": SITE["base"] + b["out"]} for i, b in enumerate(bereiche)]}}]
    render("bereiche.html", "bereiche.html", nav="bereiche", crumbs=crumbs, bereiche=bereiche, camper=camper,
           meta_title="Camper-Ausrüstung nach Bereich: 16 Themen | VanKompass",
           meta_desc="Alle Bereiche der Camper-Ausrüstung auf einen Blick: Strom, Solar, Schlafen, Sanitär, Küche, Wasser, Heizung, Sicherheit, Internet und mehr. Mit Tests, Ratgebern und Empfehlungen.",
           og_image="img/thumb-aferiy-p180-pro.svg", jsonld=jsonld(graph))

    # Camper-Hub
    crumbs = [{"name": "Start", "url": ""}, {"name": "Camper", "url": "camper.html"}]
    graph = [crumbs_ld(crumbs), {"@type": "CollectionPage", "@id": SITE["base"] + "camper.html", "name": "Camper-Ausrüstung nach Modell",
             "url": SITE["base"] + "camper.html", "isPartOf": {"@id": SITE["base"] + "#site"},
             "mainEntity": {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": c["name"], "url": SITE["base"] + c["out"]} for i, c in enumerate(camper)]}}]
    render("camper.html", "camper.html", nav="camper", crumbs=crumbs, bereiche=bereiche, camper=camper,
           meta_title="Camper-Ausrüstung nach Modell: California, Nugget, Marco Polo | VanKompass",
           meta_desc="Ausrüstung, Tests und Tipps für dein Camper-Modell: VW California, Grand California, Ford Nugget, Marco Polo, Pössl, Knaus und Sprinter-Ausbau. Passgenau statt pauschal.",
           og_image="img/thumb-aferiy-p180-pro.svg", jsonld=jsonld(graph))

    # Magazin-Beitraege (Artikel)
    cmap = {c["slug"]: c for c in camper}
    for a in beitraege:
        b = next(x for x in bereiche if x["slug"] == a["bereich"])
        cl = [cmap[sl] for sl in a.get("camper", []) if sl in cmap]
        crumbs = [{"name": "Start", "url": ""}, {"name": "Magazin", "url": "magazin.html"}, {"name": b["name"], "url": b["out"]}, {"name": a.get("crumb", a["title"]), "url": a["out"]}]
        related = [p for p in sort_posts(b["beitraege"]) if p["status"] == "live" and p["slug"] != a["slug"]][:2]
        weiterlesen = ([{"url": b["out"], "text": f'Bereich {b["h1"]}: Empfehlung, Beiträge, FAQ'}]
                       + [{"url": c["out"], "text": f'Alles zum {c["name"]}'} for c in cl]
                       + [{"url": p["url"], "text": p["title"]} for p in related]
                       + [{"url": f'magazin.html#{b["slug"]}', "text": f'Alle Beiträge zu {b["kurzname"]} im Magazin'}, {"url": "bereiche.html", "text": "Alle Bereiche"}])
        v = a["video"]
        yt_img = f'https://img.youtube.com/vi/{v["id"]}/maxresdefault.jpg'
        graph = [crumbs_ld(crumbs),
                 {"@type": "Organization", "@id": SITE["base"] + "#org", "name": "VanKompass", "url": SITE["base"], "logo": {"@type": "ImageObject", "url": SITE["base"] + "favicon.svg"}},
                 {"@type": "Article", "headline": a["title"], "description": a["meta_desc"], "image": yt_img,
                  "mainEntityOfPage": {"@type": "WebPage", "@id": SITE["base"] + a["out"]},
                  "datePublished": a["datum"], "dateModified": a.get("geaendert", a["datum"]),
                  "author": {"@type": "Organization", "name": "VanKompass"}, "publisher": {"@id": SITE["base"] + "#org"},
                  "video": {"@type": "VideoObject", "name": v["title"], "description": v["beschreibung"], "thumbnailUrl": yt_img, "uploadDate": v["upload"],
                            "duration": v["dauer_iso"], "contentUrl": f'https://www.youtube.com/watch?v={v["id"]}', "embedUrl": f'https://www.youtube-nocookie.com/embed/{v["id"]}'}},
                 faq_ld(a["faq"])]
        render("artikel.html", a["out"], a=a, bereich=b, camper_list=cl, weiterlesen=weiterlesen, nav="magazin", crumbs=crumbs,
               meta_title=a["meta_title"], meta_desc=a["meta_desc"], og_image=yt_img, og_type="article", jsonld=jsonld(graph))

    # Weiterleitungen alter URLs
    for old, target in {"silo-strom.html": "strom.html", "magazin-strom.html": "magazin.html#strom"}.items():
        write(old, env.get_template("redirect.html").render(target=target))
        written.append(old)

    # Sitemap, robots.txt, IndexNow-Schluessel
    today = datetime.date.today().isoformat()
    mod = {a["out"]: a.get("geaendert", a["datum"]) for a in beitraege}
    pages = [w for w in written if w not in ("silo-strom.html", "magazin-strom.html")]
    urls = "".join(f"  <url><loc>{SITE['base']}{'' if p == 'index.html' else p}</loc><lastmod>{mod.get(p, today)}</lastmod></url>\n" for p in pages)
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "</urlset>\n")
    write("robots.txt", f"User-agent: *\nAllow: /\nDisallow: /freebies/\nDisallow: /tools/\nDisallow: /lp-camper-strom-checkliste.html\n\nSitemap: {SITE['base']}sitemap.xml\n")
    write(SITE["indexnow_key"] + ".txt", SITE["indexnow_key"])
    written += ["sitemap.xml", "robots.txt"]

    print(f"{len(written)} Seiten geschrieben:", ", ".join(written))




if __name__ == "__main__":
    main()
