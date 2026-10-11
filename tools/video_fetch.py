#!/usr/bin/env python3
"""Holt Metadaten und deutsches Transkript eines YouTube-Videos.
Aufruf: python3 tools/video_fetch.py <youtube-url-oder-id> <ausgabe.json>"""
import json
import re
import sys
import urllib.parse
import urllib.request

sys.path.insert(0, "/Users/twentyseconds/Library/Python/3.9/lib/python/site-packages")
from youtube_transcript_api import YouTubeTranscriptApi  # noqa: E402

MONATE = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember"]


def video_id(s):
    m = re.search(r"(?:v=|youtu\.be/|shorts/|embed/)([A-Za-z0-9_-]{11})", s)
    return m.group(1) if m else s.strip()


def fetch(url, headers=None):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept-Language": "de-DE,de", **(headers or {})})
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")


def main(arg, out):
    vid = video_id(arg)
    o = json.loads(fetch(f"https://www.youtube.com/oembed?url={urllib.parse.quote('https://www.youtube.com/watch?v=' + vid)}&format=json"))
    html = fetch(f"https://www.youtube.com/watch?v={vid}&hl=de")

    def find(k, default=None):
        m = re.search(r'"%s":"([^"]*)"' % k, html)
        return m.group(1) if m else default

    secs = int(find("lengthSeconds", "0"))
    upload = (find("publishDate") or find("uploadDate") or "")[:10]
    y, mo, d = (upload.split("-") + ["", "", ""])[:3]
    m_abo = re.search(r'"subscriberCountText":\{"accessibility":\{"accessibilityData":\{"label":"([^"]*)"', html)
    m_desc = re.search(r'"shortDescription":"((?:[^"\\]|\\.)*)"', html)
    desc = json.loads('"' + m_desc.group(1) + '"') if m_desc else ""
    werbung = bool(re.search(r'"paidContentOverlay"|Enthält bezahlte Werbung|bezahlte Promotion|isPaidPromotion', html))

    api = YouTubeTranscriptApi()
    langs = [t.language_code for t in api.list(vid)]
    pref = [l for l in ("de", "de-DE") if l in langs] or langs[:1]
    segs = [{"t": round(x.start), "text": x.text} for x in api.fetch(vid, languages=pref)] if pref else []

    data = {
        "id": vid,
        "url": f"https://www.youtube.com/watch?v={vid}",
        "title": o["title"],
        "kanal": o["author_name"],
        "kanal_url": o["author_url"],
        "kanal_kuerzel": "".join(w[0] for w in re.findall(r"[A-Za-z0-9]+", o["author_name"]))[:3].upper(),
        "abonnenten": m_abo.group(1) if m_abo else "",
        "upload": upload,
        "upload_text": f"{int(d)}. {MONATE[int(mo) - 1]} {y}" if upload else "",
        "dauer_sek": secs,
        "dauer_iso": f"PT{secs // 60}M{secs % 60}S",
        "dauer_text": f"{secs // 60}:{secs % 60:02d} Min.",
        "aufrufe": find("viewCount", ""),
        "beschreibung": desc,
        "werbung_marker": werbung,
        "transkript_sprache": pref[0] if pref else None,
        "transkript": segs,
        "transkript_text": " ".join(x["text"] for x in segs),
    }
    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print(json.dumps({k: v for k, v in data.items() if k not in ("transkript", "transkript_text", "beschreibung")}, ensure_ascii=False, indent=1))
    print(f"Transkript: {len(segs)} Segmente, {len(data['transkript_text'].split())} Wörter -> {out}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
