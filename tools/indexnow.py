#!/usr/bin/env python3
"""Meldet URLs per IndexNow (Bing, Yandex, DuckDuckGo, Naver, Seznam) an.
Aufruf: python3 tools/indexnow.py <url-oder-pfad> [...]   Pfade wie 'strom.html' werden zu vollen URLs."""
import json
import os
import sys
import time
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from build import SITE  # noqa: E402


def main(args):
    urls = [u if u.startswith("http") else SITE["base"] + ("" if u == "index.html" else u) for u in args]
    key_url = f'{SITE["base"]}{SITE["indexnow_key"]}.txt'
    try:
        live = urllib.request.urlopen(key_url, timeout=20).read().decode().strip()
    except Exception as e:
        live = f"FEHLER {e}"
    if live != SITE["indexnow_key"]:
        print(f"IndexNow abgebrochen: Schluesseldatei nicht live oder falsch ({key_url}: {live[:40]}). Erst deployen, dann pingen.")
        return 1
    body = json.dumps({"host": SITE["base"].split("//")[1].strip("/"), "key": SITE["indexnow_key"],
                       "keyLocation": f'{SITE["base"]}{SITE["indexnow_key"]}.txt', "urlList": urls}).encode()
    req = urllib.request.Request("https://api.indexnow.org/indexnow", data=body, headers={"Content-Type": "application/json; charset=utf-8"})
    for versuch in range(1, 5):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                print(f"IndexNow: HTTP {r.status} fuer {len(urls)} URL(s)")
                break
        except urllib.error.HTTPError as e:
            # 403 kommt kurz nach einem Deploy vor, wenn der Validierer die Schluesseldatei mitten im Upload abruft
            if e.code == 403 and versuch < 4:
                print(f"IndexNow: HTTP 403, Versuch {versuch} von 4, warte 45 s ...")
                time.sleep(45)
                continue
            print(f"IndexNow: HTTP {e.code} {e.reason}")
            return 1
    for u in urls:
        print("  ", u)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
