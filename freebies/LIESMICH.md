# VanKompass Freebies (16 Bereiche)

Eine Lead-Magnet-Familie für die 16 Vanlife-Bereiche. Regel: 1 Bereich = 1 Freebie, innerhalb des Bereichs für alle Artikel identisch. Modell-Hubs (z.B. VW California) tragen bewusst kein Freebie.

## Inhalt dieses Ordners

| Datei / Ordner | Zweck |
|---|---|
| `freebies-data.json` | Single Source of Truth: alle 16 Freebie-Inhalte als JSON (bereinigt, mit echten Umlauten, dedupliziert) |
| `clean/*.json` | Pro-Bereich-Dateien aus der Bereinigung (Quelle für `freebies-data.json`) |
| `freebie-styles.css` | Gemeinsames Print-Stylesheet (A4, VanKompass-CI). Eine Quelle = garantiert identische CI |
| `build-freebies.py` | Generator: liest Daten + CSS, schreibt 16 HTML-Freebies + `index.html`. Mit `--pdf` zusätzlich PDFs via Chrome headless |
| `freebie-<silo>.html` | Die 16 gebauten Freebie-Seiten |
| `pdf/freebie-<silo>.pdf` | Die 16 gerenderten PDFs |
| `index.html` | Übersichtskachel-Seite über alle 16 Freebies |
| `BREVO-KONVENTIONEN.md` | Verbindliches Schema für Brevo (Liste, Attribut, Merge-Feld, DOI-Flow) |

## Build

```
python3 build-freebies.py          # nur HTML + Index
python3 build-freebies.py --pdf    # zusätzlich PDFs (braucht Google Chrome)
```

## Die 16 Freebies (in der Reihenfolge der Bereiche)

1. **Cockpit** — Ordnung im Fahrerhaus: Cockpit-Checkliste plus Mess-Merkblatt
2. **Strom** — Die Camper-Strom-Checkliste: Verbrauch ankreuzen, Batteriegröße ausrechnen
3. **Solar** — Solar-Spickzettel: Wie viel Watt brauche ich wirklich?
4. **Schlafen** — Die Camper-Schlaf-Checkliste: Gut schlafen, trocken bleiben, richtig messen
5. **Sanitär** — Trockentrenntoilette oder nicht? Die Entscheidungshilfe für dein Camper-Klo
6. **Küche** — Die Camper-Küchen-Packliste plus Kühlbox-Energie-Faustformel
7. **Wasser** — Der Wassersystem-Planer: Tank, Pumpe, Filter und Liter-Bedarf
8. **Heizung** — Der Standheizungs-Spickzettel: kW wählen, Verbrauch abschätzen, sicher einbauen
9. **Verdunkelung** — Dunkel schlafen, mückenfrei lüften: Mess- und Auswahl-Checkliste
10. **Stauraum** — Die Stauraum-Optimierungs-Checkliste: Mehr Liter, sicheres Gewicht
11. **Außenbereich** — Markise oder Vorzelt: Die Auswahlhilfe
12. **Sicherheit** — Die Camper-Sicherheits-Checkliste: Diebstahlschutz in vier Ebenen
13. **Internet** — Online im Funkloch: Die Internet-Entscheidungshilfe
14. **Apps** — Die Camper-App-Toolbox: Welche App für welche Aufgabe
15. **Sitze** — Aus Fahrersitz wird Wohn-Sessel: Drehkonsolen-Passungs-Checkliste
16. **Sound** — Sound und Entertainment: Setup-Checkliste

## Wie die CI technisch garantiert ist

Es gibt **eine** Vorlage (`freebie-styles.css`) und **einen** Generator (`build-freebies.py`). Alle 16 Freebies entstehen aus identischen Bausteinen, nur die Inhalte aus `freebies-data.json` ändern sich. Das heißt: CI-Drift ist ausgeschlossen, Änderungen am Layout treffen automatisch alle 16, neue Bereiche brauchen nur einen JSON-Eintrag.

## Aus der QA übernommen

- **Umlaute:** Alle 16 wurden auf echte deutsche Umlaute (ä ö ü ß) bereinigt. Fließtext-Stichproben sauber.
- **Dedup:** Die Wattstunden-Faustformel ist nur noch in der Strom-Checkliste vollständig ausgeführt. Solar, Küche, Sound verweisen darauf.
- **Brevo:** Schema vereinheitlicht in `BREVO-KONVENTIONEN.md` (eine Liste, Attribut `BEREICH`, Merge-Feld `{{contact.VORNAME}}`).

## Strategischer Hinweis aus der QA

Die zwei schwächsten Bereiche für Affiliate-Tiefe sind laut QA **Apps** und **Sound**. Die Freebies sind solide, aber dahinter steht weniger Kaufentscheidung als bei den Kern-Silos. Für die Reihenfolge des Cluster-Ausbaus relevant, nicht für die Freebie-Produktion.

## Hinweis zum Gating

Die PDFs liegen aktuell offen unter `pdf/`. Sobald wir live monetarisieren, müssen sie hinter den Brevo-DOI-Flow (oder ein nicht erratbares Verzeichnis), sonst umgeht der Nutzer die E-Mail-Anmeldung. Details in `BREVO-KONVENTIONEN.md`.
