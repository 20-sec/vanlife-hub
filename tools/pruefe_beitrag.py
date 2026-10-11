#!/usr/bin/env python3
"""Prueft einen Magazin-Beitrag (data/beitraege/<slug>.json) und, falls gebaut, die erzeugte HTML-Seite.
Aufruf: python3 tools/pruefe_beitrag.py <slug>   -> Exit 0 wenn alles passt."""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
SKIP = {"slug", "out", "url", "thumb", "id", "kanal_url", "bereich", "camper", "kanal_kuerzel", "dauer_iso", "datum", "upload", "geaendert"}
OK_PREFIX = ("bequem", "quell", "zuerst", "kabelquer", "thermoelektr", "quer", "frequen", "sequen", "konsequen", "aqua", "manuell", "aktuell",
             "individuell", "eventuell", "virtuell", "visuell", "duell", "poet", "koeff", "aero", "israel", "michael", "bluetooth", "steuer",
             "neue", "dauer", "genau", "bau", "feuer", "trauer", "mauer", "sauer", "frau", "schau", "kau", "grau", "vertrau", "lau", "due", "que")


def texts(o, key=None):
    if isinstance(o, str):
        if key not in SKIP:
            yield o
    elif isinstance(o, dict):
        for k, v in o.items():
            yield from texts(v, k)
    elif isinstance(o, list):
        for v in o:
            yield from texts(v, key)


def words(html):
    return len(re.sub(r"<[^>]+>", " ", html).split())


def main(slug):
    errs = []
    path = f"data/beitraege/{slug}.json"
    if not os.path.exists(path):
        print("FEHLT:", path); return 1
    a = json.load(open(path, encoding="utf-8"))
    for k in ("slug", "out", "bereich", "camper", "kategorie", "title", "meta_title", "meta_desc", "teaser", "lead_teaser", "datum", "datum_text", "thumb", "video", "answer", "sections", "faq", "transparenz"):
        if k not in a:
            errs.append(f"Feld fehlt: {k}")
    if errs:
        print("\n".join(errs)); return 1
    if a["slug"] != slug: errs.append("slug stimmt nicht mit Dateiname ueberein")
    if not a["out"].startswith(f"magazin-{a['bereich']}-"): errs.append(f"out sollte mit magazin-{a['bereich']}- beginnen")
    if not os.path.exists(f"data/fragments/bereich-{a['bereich']}.json"): errs.append(f"unbekannter Bereich {a['bereich']}")
    for c in a["camper"]:
        if not os.path.exists(f"data/fragments/camper-{c}.json"): errs.append(f"unbekannter Camper {c}")
    if len(a["meta_title"]) > 60: errs.append(f"meta_title {len(a['meta_title'])} Zeichen (max 60)")
    if not 120 <= len(a["meta_desc"]) <= 160: errs.append(f"meta_desc {len(a['meta_desc'])} Zeichen (120 bis 160)")
    if not 50 <= len(a["title"]) <= 80: errs.append(f"title {len(a['title'])} Zeichen (50 bis 80)")
    if not 90 <= len(a["teaser"]) <= 140: errs.append(f"teaser {len(a['teaser'])} Zeichen (90 bis 140)")
    if not 45 <= words(a["lead_teaser"]) <= 75: errs.append(f"lead_teaser {words(a['lead_teaser'])} Woerter (45 bis 75)")
    if not 40 <= words(a["answer"]) <= 70: errs.append(f"answer {words(a['answer'])} Woerter (40 bis 70)")
    if not 4 <= len(a["sections"]) <= 9: errs.append(f"{len(a['sections'])} Abschnitte (4 bis 9)")
    ids = [s.get("id") for s in a["sections"]]
    if len(ids) != len(set(ids)) or not all(ids): errs.append("Abschnitts-IDs fehlen oder doppelt")
    for s in a["sections"]:
        if not s.get("h2") or (not s.get("html") and not s.get("specs")): errs.append(f"Abschnitt {s.get('id')} ohne h2 oder Inhalt")
    if not 5 <= len(a["faq"]) <= 9: errs.append(f"{len(a['faq'])} FAQ (5 bis 9)")
    for f in a["faq"]:
        n = sum(words(p) for p in f["a"])
        if not 40 <= n <= 220: errs.append(f"FAQ '{f['q'][:40]}' {n} Woerter (40 bis 220)")
        if not f["q"].endswith("?"): errs.append(f"FAQ-Frage ohne Fragezeichen: {f['q'][:40]}")
    v = a["video"]
    for k in ("id", "title", "kanal", "kanal_url", "upload", "upload_text", "dauer_iso", "dauer_text", "beschreibung"):
        if not v.get(k): errs.append(f"video.{k} fehlt")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", a["datum"]): errs.append("datum nicht YYYY-MM-DD")
    if not os.path.exists(a["thumb"]): errs.append(f"Thumbnail fehlt: {a['thumb']}")
    txt = " ".join(texts(a))
    if "—" in txt or "–" in txt: errs.append("Gedankenstrich gefunden")
    if re.search(r"[\U0001F300-\U0001FAFF☀-➿]", txt): errs.append("Emoji gefunden")
    if re.search(r"\*\*|`", txt): errs.append("Markdown-Zeichen gefunden")
    sus = sorted({w for w in re.findall(r"\b\w+\b", txt) if re.search(r"(?<![aeiouAEIOU])(ae|oe|ue)", w) and not w.lower().startswith(OK_PREFIX)})
    if sus: errs.append("Ersatzschreibung? " + ", ".join(sus[:8]))

    html_path = a["out"]
    if os.path.exists(html_path):
        h = open(html_path, encoding="utf-8").read()
        for ld in re.findall(r'<script type="application/ld\+json">(.*?)</script>', h, flags=re.S):
            try: json.loads(ld)
            except Exception as e: errs.append(f"JSON-LD ungueltig: {e}")
        for href in set(re.findall(r'href="([^"#?]+\.html)', h)):
            if not href.startswith("http") and not os.path.exists(href): errs.append(f"toter Link: {href}")
        if "noindex" in h: errs.append("noindex in HTML")
        if 'youtube-nocookie.com/embed/' + v["id"] not in h: errs.append("Video-Embed fehlt")
    else:
        print("Hinweis: HTML noch nicht gebaut, nur Daten geprueft.")

    if errs:
        print(f"{len(errs)} Problem(e) in {slug}:"); [print("  -", e) for e in errs]; return 1
    print(f"{slug}: alle Pruefungen bestanden."); return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
