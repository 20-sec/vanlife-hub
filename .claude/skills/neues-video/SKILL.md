---
name: neues-video
description: Nimmt ein YouTube-Video als neuen Magazin-Beitrag auf vankompass.de auf. Fragt nur nach der Video-URL, danach läuft alles automatisch durch: Transkript, Beitrag mit SEO und AEO, FAQ, interne Verlinkung, Faktenprüfung, Build, Deploy in beide Repos, Indexierung. Aufruf mit /neues-video oder /neues-video <youtube-url>.
---

# Neues Video als Magazin-Beitrag aufnehmen

Du arbeitest im Projektordner `vankompass` (Wurzel mit `build.py`). Es gibt **genau eine Rückfrage**: die YouTube-URL, falls sie nicht im Aufruf steht. Danach keine weiteren Fragen; triff bei Unklarheiten die beste Annahme und nenne sie im Abschlussbericht. Der Beitrag geht ohne Freigabe live.

## Schritt 0: URL

Fehlt die URL im Aufruf, frag kurz danach (AskUserQuestion oder Klartext). Sonst sofort weiter.

## Schritt 1: Video holen

```bash
python3 tools/video_fetch.py "<URL>" /tmp/vk-video.json
```

Lies danach `/tmp/vk-video.json` (Metadaten + `transkript_text`). Bricht das Transkript ab (kein deutsches Transkript, API-Fehler), nutze das englische, falls vorhanden; sonst Abbruch mit klarer Meldung.

## Schritt 2: Einordnen

Aus Titel, Beschreibung und Transkript bestimmen:

- **Bereich** (ein Slug aus `data/fragments/bereich-*.json`): strom, solar, schlafen, sanitaer, kueche, wasser, heizung, verdunkelung, cockpit, stauraum, aussenbereich, sicherheit, internet, camper-apps, sitze, sound. Bei zwei passenden Bereichen: der, in dem das Produkt gekauft würde.
- **Camper** (Liste, darf leer sein): vw-california, vw-grand-california, ford-nugget, marco-polo, poessl-ducato, knaus, sprinter-ausbau. Nur nennen, wenn das Modell im Video konkret vorkommt.
- **Kategorie**: Video-Test (Produkt wird getestet), Ratgeber, Vergleich, Praxis, Rechenbeispiel, Checkliste.
- **Slug**: kurz, ASCII, Bindestriche, Produkt plus Kontext (Muster `aferiy-p180-pro-ford-nugget`). Dateiname: `magazin-<bereich>-<slug>.html`.
- **Top-Beitrag**: `"top": true` nur, wenn der Bereich noch keinen Live-Beitrag hat (prüfe `data/beitraege/*.json` auf gleichen `bereich`). Sonst `"top": false`. Der Top-Beitrag wird später händisch gewechselt, nie automatisch.

## Schritt 3: Beitrag schreiben

Erzeuge `data/beitraege/<slug>.json` **exakt nach dem Schema** von `data/beitraege/aferiy-p180-pro-ford-nugget.json` (lies es zuerst vollständig). Alle Felder, die dort vorkommen, müssen vorkommen.

Inhaltliche Regeln:

- **Nur, was im Video oder in den Herstellerdaten steht.** Jede Zahl, jeder Messwert, jede Aussage stammt aus dem Transkript. Keine ergänzten "Erfahrungswerte", keine erfundenen Preise, keine Testergebnisse, die das Video nicht zeigt. Formuliere "laut dem Tester", "im Video", "laut Hersteller".
- **Neutral.** VanKompass bewertet nicht selbst, es fasst zusammen. Kanal und Video werden genannt und verlinkt. Werbekennzeichnung übernehmen (`video.werbung`), wenn `werbung_marker` true ist oder das Transkript es sagt; sonst `null`.
- **Sprache:** Deutsch, Du-Form, echte Umlaute, keine Gedankenstriche (weder – noch —), keine Emojis, kein Markdown in Texten. HTML in `sections[].html` nur mit: `<p>`, `<ul><li>`, `<h3>`, `<strong>`, `<div class="praxis"><h4>…</h4><p>…</p></div>`, `<div class="nope"><h4>…</h4><ul>…</ul></div>`, `<div class="fazit"><h2 style="font-size:22px;">…</h2><p>…</p></div>`.
- **SEO:** `title` 50 bis 80 Zeichen mit Produkt, Camper und Nutzen; `meta_title` maximal 60 Zeichen; `meta_desc` 120 bis 160 Zeichen; H2-Überschriften als Suchphrasen.
- **AEO:** `answer` 40 bis 70 Wörter, steht allein, enthält die wichtigsten Zahlen (`<strong>` erlaubt). `lead_teaser` 45 bis 75 Wörter, `teaser` 90 bis 140 Zeichen.
- **Abschnitte:** 5 bis 8. Immer dabei: "Was zeigt das Video?", technische Daten als `specs` (6 bis 8 Karten, nur belegte Werte) plus `specs_note` mit Quelle und Stand, Praxis im Camper, Fazit aus dem Video (als `.fazit`-Box, mit Hinweis auf Werbekennzeichnung, falls vorhanden). Weitere Abschnitte nach Inhalt.
- **FAQ:** 6 bis 8 Fragen, wie Menschen sie googeln. Jede Antwort 2 bis 3 Absätze, zusammen 60 bis 200 Wörter: erst die direkte Antwort, dann Zahlen und Kontext aus dem Video, dann Praxis. `faq_thema` wie "zur <Produktname>".
- **Interne Verlinkung** entsteht automatisch (Bereich, Camper, verwandte Beiträge, Magazin). Nichts im JSON dafür nötig.
- `datum` = heute, `datum_text` = "Monat Jahr", `geaendert` = heute, `thumb` = `img/thumb-<slug>.svg`.

## Schritt 4: Thumbnail

Typografisch, zwei Zeilen mit je maximal 24 Zeichen, Tag = Kategorie:

```bash
python3 -c "from build import thumb_svg, write; write('img/thumb-<slug>.svg', thumb_svg('<Zeile 1>', '<Zeile 2>', '<Kategorie>'))"
```

## Schritt 5: Faktenprüfung durch einen zweiten Agenten

Starte einen Agenten (Agent-Tool, general-purpose, im Vordergrund), Auftrag sinngemäß:

> Lies `data/beitraege/<slug>.json` und `/tmp/vk-video.json`. Prüfe jede Zahl, jeden Messwert und jede Tatsachenbehauptung im Beitrag (answer, sections, specs, faq) gegen `transkript_text` und `beschreibung`. Liste jede Aussage, die im Transkript nicht belegt ist oder ihm widerspricht, mit Zitat der Transkriptstelle bzw. "nicht belegt". Prüfe außerdem, ob der Beitrag etwas Wichtiges aus dem Video verschweigt (Einschränkungen, Kritik, Grenzen). Keine Stilkritik. Unter 300 Wörtern.

Jede nicht belegte Aussage: korrigieren oder streichen. Fehlende Kritikpunkte: ergänzen. Dann Datei erneut speichern.

## Schritt 6: Prüfen und bauen

```bash
python3 tools/pruefe_beitrag.py <slug> && python3 build.py && python3 tools/pruefe_beitrag.py <slug>
```

Der erste Lauf prüft die Daten, der zweite zusätzlich das gebaute HTML (JSON-LD, Links, Embed). Alle gemeldeten Probleme beheben und wiederholen, bis "alle Pruefungen bestanden" erscheint. Danach die Seite einmal im Browser öffnen (preview_start mit `http://localhost:8765/magazin-<bereich>-<slug>.html`, falls ein Server läuft, sonst `python3 -m http.server 8765` im Hintergrund starten) und per Screenshot sichten: Video-Embed, Spec-Karten, FAQ, Weiterlesen-Leiste müssen sichtbar sein.

## Schritt 7: Deploy

```bash
bash tools/deploy.sh "Neuer Beitrag: <Titel>" magazin-<bereich>-<slug>.html
```

Baut, committet und pusht in beide Repos und wartet, bis die Seite live und in der Sitemap ist.

## Schritt 8: Indexierung

```bash
python3 tools/indexnow.py magazin-<bereich>-<slug>.html <bereich>.html magazin.html index.html bereiche.html camper-<slug>.html ...
```

Alle Seiten melden, auf denen der Beitrag jetzt erscheint (Artikel, Bereichs-Portal, Magazin, Startseite, Bereiche-Übersicht, betroffene Camper-Portale). Google hat keinen IndexNow-Anschluss; die Sitemap ist aktualisiert und wird von der Search Console gelesen.

## Schritt 9: Abschlussbericht an Markus

Kurz, auf Deutsch, per Du:

- Live-Link des Beitrags
- Getroffene Annahmen: Bereich, Camper, Kategorie, ob Top-Beitrag
- Ergebnis der Faktenprüfung (was gestrichen oder korrigiert wurde)
- Hinweis: Für Google sofort anstoßen unter https://search.google.com/search-console (URL-Prüfung, "Indexierung beantragen").
- Falls das Video ein Produkt behandelt, das noch keine Empfehlung im Bereich ist: ein Satz, ob es als Empfehlung taugt (nur Hinweis, keine Änderung).
