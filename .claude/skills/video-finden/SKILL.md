---
name: video-finden
description: Findet die Lücken im VanKompass-Magazin (Bereiche und Camper ohne oder mit wenigen Beiträgen), leitet daraus deutsche YouTube-Suchphrasen ab, durchsucht YouTube, filtert auf deutsche Sprache, Mindestlänge und Aktualität und schlägt vier bis fünf Videos vor. Nach Markus' Auswahl läuft für jedes gewählte Video der Ablauf aus /neues-video. Aufruf mit /video-finden, optional mit Bereich oder Camper, z. B. /video-finden sound.
---

# Videos für Magazin-Lücken finden

Du arbeitest im Projektordner `vankompass` (Wurzel mit `build.py`). Der Ablauf hat **genau einen Stopp**: nach den Vorschlägen. Vorher keine Rückfragen; triff Annahmen und nenne sie.

## Schritt 1: Lücken ermitteln

```bash
python3 tools/video_suche.py luecken
```

Die Ausgabe listet Bereiche und Camper, sortiert nach Zahl der Live-Beiträge, mit den bereits geplanten Beitragstiteln aus den Fragmenten. Priorität: **zuerst Bereiche mit 0 Beiträgen, dann Bereiche mit 1, dann Camper mit 0.** Hat Markus beim Aufruf einen Bereich oder Camper genannt, gilt nur dieser.

Wähle für diesen Lauf die **zwei bis drei dringendsten Lücken**. Mehr nicht, sonst wird die Vorschlagsliste unübersichtlich.

## Schritt 2: Deutsche Suchphrasen ableiten

Pro Lücke zwei bis drei Suchphrasen, **immer auf Deutsch**, so formuliert, wie Menschen bei YouTube suchen: Produktgattung plus Camper-Kontext plus Absicht. Beispiele: "Markise Wohnmobil Montage", "Starlink Wohnmobil Erfahrung", "Bluetooth Lautsprecher Camper Test", "Campingstuhl Test Wohnmobil". Die geplanten Beitragstitel aus Schritt 1 sind gute Vorlagen, weil sie schon Suchphrasen sind. Markennamen nur, wenn sie das Thema tragen.

## Schritt 3: YouTube durchsuchen

Für jede Phrase:

```bash
python3 tools/video_suche.py suche "<Phrase>"
```

Das Werkzeug filtert automatisch: keine Shorts, mindestens 8 Minuten, höchstens 2 Jahre alt, deutsches Transkript vorhanden, nicht bereits verarbeitet, nicht auf der Merkliste. Liefert eine Phrase weniger als zwei Treffer, versuche eine Variante (anderes Nomen, "Erfahrung" statt "Test", "Wohnmobil" statt "Camper"). Bei dünnen Themen darf `--max-jahre 4` gesetzt werden; das im Vorschlag nennen.

## Schritt 4: Bewerten und vier bis fünf Vorschläge auswählen

Reihenfolge der Kriterien:
1. Passt das Video zur Lücke **und** zur Suchphrase, auf die der Beitrag zielen soll (Titel und Kanal lassen das erkennen)?
2. Länge 10 bis 30 Minuten ist ideal; sehr lange Videos nur, wenn das Thema es trägt.
3. Jünger ist besser; über 18 Monate nur, wenn nichts Jüngeres passt.
4. Aufrufe als Hinweis auf Nachfrage, nicht als Hauptkriterium.
5. Ein Kanal höchstens zweimal in der Liste.

Pro Lücke mindestens ein Vorschlag. Nicht mehr als fünf insgesamt.

## Schritt 5: Vorschläge zeigen und STOPP

Zeige Markus die Liste, nummeriert, pro Video:
- Titel, Kanal, Dauer, Alter, Aufrufe, URL
- Lücke, die es schließt (Bereich oder Camper)
- Keyword-Phrase, auf die der Beitrag zielen würde
- Ein Satz: warum dieses Video

Dann fragen: "Welche sollen rein? Nummern nennen, oder 'alle', oder 'keins'." Nichts weiter tun, bis Markus antwortet.

## Schritt 6: Auswahl verarbeiten

- Für jedes **gewählte** Video den kompletten Ablauf aus `.claude/skills/neues-video/SKILL.md` ausführen (Transkript, Beitrag, Faktenprüfung, Build, Deploy, IndexNow). Bei mehreren Videos die Schreib- und Prüfschritte parallel über Agenten, Build und Deploy einmal gemeinsam am Ende, wie in dieser Session eingeübt. Top-Beitrag-Regel beachten: erster Live-Beitrag eines Bereichs bekommt `"top": true`, sonst `false`.
- Für jedes **nicht gewählte** Video:

```bash
python3 tools/video_suche.py merken <video-id> "von Markus abgelehnt am <Datum>"
```

Damit taucht es nie wieder in einer Vorschlagsliste auf.

## Schritt 7: Abschlussbericht

Kurz, auf Deutsch, per Du: Live-Links der neuen Beiträge, welche Lücken damit geschlossen sind, welche noch offen bleiben, und der Hinweis auf die Google Search Console für die Indexierung.
