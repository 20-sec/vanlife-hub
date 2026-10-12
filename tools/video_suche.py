#!/usr/bin/env python3
"""Findet Luecken im Magazin und passende deutsche YouTube-Videos dafuer.

  python3 tools/video_suche.py luecken                 Bereiche und Camper nach Zahl der Live-Beitraege
  python3 tools/video_suche.py suche "Suchphrase" [--min-minuten 8] [--max-jahre 2] [--ohne-transkript-check]
  python3 tools/video_suche.py merken <video-id> [Grund]   Video dauerhaft nicht mehr vorschlagen
  python3 tools/video_suche.py merkliste                Merkliste anzeigen

Benutzte Videos (data/beitraege) und gemerkte Videos (data/merkliste-videos.json) werden bei der Suche ausgelassen."""
import datetime
import glob
import json
import os
import re
import sys
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT)
sys.path.insert(0, ROOT)
sys.path.insert(0, "/Users/twentyseconds/Library/Python/3.9/lib/python/site-packages")
from build import BEREICH_ORDER, CAMPER_ORDER  # noqa: E402

MERKLISTE = "data/merkliste-videos.json"


def lade_merkliste():
    return json.load(open(MERKLISTE, encoding="utf-8")) if os.path.exists(MERKLISTE) else {}


def benutzte_ids():
    return {json.load(open(f, encoding="utf-8"))["video"]["id"] for f in glob.glob("data/beitraege/*.json")}


def luecken():
    arts = [json.load(open(f, encoding="utf-8")) for f in glob.glob("data/beitraege/*.json")]
    frag = {}
    for f in glob.glob("data/fragments/*.json"):
        d = json.load(open(f, encoding="utf-8"))
        frag[(d["typ"], d["slug"])] = d
    out = {"bereiche": [], "camper": []}
    for s in BEREICH_ORDER:
        d = frag[("bereich", s)]
        n = sum(1 for a in arts if a["bereich"] == s)
        out["bereiche"].append({"slug": s, "name": d["name"], "live": n, "kurz": d["kurz"],
                                "geplante_titel": [p["title"] for p in d["beitraege"] if p.get("status") != "live"][:6]})
    for s in CAMPER_ORDER:
        d = frag[("camper", s)]
        n = sum(1 for a in arts if s in a.get("camper", []))
        out["camper"].append({"slug": s, "name": d["name"], "live": n,
                              "geplante_titel": [p["title"] for p in d["beitraege"] if p.get("status") != "live"][:4]})
    out["bereiche"].sort(key=lambda x: x["live"])
    out["camper"].sort(key=lambda x: x["live"])
    return out


def _txt(x):
    if not x:
        return ""
    return x.get("simpleText") or "".join(r.get("text", "") for r in x.get("runs", []))


def _walk(o):
    if isinstance(o, dict):
        if "videoRenderer" in o:
            yield o["videoRenderer"]
        for v in o.values():
            yield from _walk(v)
    elif isinstance(o, list):
        for v in o:
            yield from _walk(v)


def _minuten(length_text):
    parts = [int(p) for p in length_text.split(":") if p.isdigit()]
    if not parts:
        return 0
    sec = 0
    for p in parts:
        sec = sec * 60 + p
    return sec / 60


def _alter_monate(published):
    m = re.search(r"vor (\d+) (Jahr|Monat|Woche|Tag|Stunde|Minute)", published)
    if not m:
        return None
    n, einheit = int(m.group(1)), m.group(2)
    return {"Jahr": n * 12, "Monat": n, "Woche": n / 4.3, "Tag": n / 30, "Stunde": 0, "Minute": 0}[einheit]


def _hat_deutsches_transkript(vid):
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        langs = [t.language_code for t in YouTubeTranscriptApi().list(vid)]
        return any(l.startswith("de") for l in langs), langs
    except Exception as e:
        return False, [type(e).__name__]


def suche(phrase, min_minuten=8.0, max_jahre=2.0, transkript_check=True, max_treffer=8):
    url = "https://www.youtube.com/results?search_query=" + urllib.parse.quote(phrase) + "&hl=de&gl=DE"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "de-DE,de"})
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")
    m = re.search(r"var ytInitialData = (\{.*?\});</script>", html, re.S)
    if not m:
        return {"phrase": phrase, "fehler": "Suchseite nicht lesbar", "treffer": []}
    benutzt, gemerkt = benutzte_ids(), lade_merkliste()
    treffer, aussortiert = [], {"zu_kurz": 0, "zu_alt": 0, "benutzt": 0, "gemerkt": 0, "kein_de_transkript": 0, "short": 0}
    for v in _walk(json.loads(m.group(1))):
        vid = v["videoId"]
        titel, laenge, alter = _txt(v.get("title")), _txt(v.get("lengthText")), _txt(v.get("publishedTimeText"))
        if not laenge:
            aussortiert["short"] += 1; continue
        if vid in benutzt:
            aussortiert["benutzt"] += 1; continue
        if vid in gemerkt:
            aussortiert["gemerkt"] += 1; continue
        minuten = _minuten(laenge)
        if minuten < min_minuten:
            aussortiert["zu_kurz"] += 1; continue
        monate = _alter_monate(alter)
        if monate is None or monate > max_jahre * 12:
            aussortiert["zu_alt"] += 1; continue
        eintrag = {"id": vid, "url": f"https://www.youtube.com/watch?v={vid}", "titel": titel, "kanal": _txt(v.get("ownerText")),
                   "dauer": laenge, "minuten": round(minuten, 1), "alter": alter, "aufrufe": _txt(v.get("viewCountText"))}
        if transkript_check:
            ok, langs = _hat_deutsches_transkript(vid)
            if not ok:
                aussortiert["kein_de_transkript"] += 1; continue
            eintrag["transkript_sprachen"] = langs
        treffer.append(eintrag)
        if len(treffer) >= max_treffer:
            break
    return {"phrase": phrase, "treffer": treffer, "aussortiert": aussortiert}


def merken(vid, grund=""):
    ml = lade_merkliste()
    ml[vid] = {"grund": grund, "datum": datetime.date.today().isoformat()}
    json.dump(ml, open(MERKLISTE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    open(MERKLISTE, "a").write("\n")
    print(f"gemerkt: {vid} ({grund or 'ohne Grund'})")


def main(argv):
    if not argv or argv[0] == "luecken":
        print(json.dumps(luecken(), ensure_ascii=False, indent=1))
    elif argv[0] == "suche":
        phrase = argv[1]
        mm = float(argv[argv.index("--min-minuten") + 1]) if "--min-minuten" in argv else 8.0
        mj = float(argv[argv.index("--max-jahre") + 1]) if "--max-jahre" in argv else 2.0
        print(json.dumps(suche(phrase, mm, mj, "--ohne-transkript-check" not in argv), ensure_ascii=False, indent=1))
    elif argv[0] == "merken":
        merken(argv[1], " ".join(argv[2:]))
    elif argv[0] == "merkliste":
        print(json.dumps(lade_merkliste(), ensure_ascii=False, indent=1))
    else:
        print(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
