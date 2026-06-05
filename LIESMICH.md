# VanKompass (Arbeitstitel) - Vanlife-Hub Entwurf

Erster baufertiger Entwurf der Vanlife-Hub-Seite (MS Phantom, Affiliate-Nischenseite). Start-Silo: Batterie/Strom. Stand: 2026-06-05.

## Was hier liegt

| Datei | Seitentyp | Zeigt |
|-------|-----------|-------|
| `index.html` | Hub-Startseite (T1) | Der "worum willst du dich kuemmern"-Waehler: 16 Bereichs-Kacheln + Camper-Modelle + Tool-Teaser. Kein Affiliate-Link. |
| `silo-strom.html` | Silo-Pillar (T2) | Bereich Batterie/Strom: Antwort-Box, Loesungstypen, Kaufkriterien als FAQ, Tool-Einstieg, kuratierte Top-3, Verteiler in die Money-Artikel. |
| `artikel-powerstation-vw-california-t61.html` | Money-Artikel (T3) | Das vollstaendige 13-Block-Template "Die besten X fuer [Modell]". Haupt-Umsatztraeger und Haupt-Zitatquelle. |
| `vanlife-config.js` | Zentrale Affiliate-Konfig | DIE EINE PFLEGESTELLE fuer alle Affiliate-IDs und die Link-Logik. |
| `vanlife-styles.css` | Layout-System | Eingefroren, mobile-first. |

## Aufmachen

Doppelklick auf `index.html` (laeuft per `file://`, kein Server noetig). Von dort durchklicken: Strom-Kachel fuehrt zur Silo-Seite, der Verteiler-Block dort zum Money-Artikel.

## So vereint der Entwurf die zwei Ziele (Umsatz UND Nutzen)

Dieselbe Struktur bedient Mensch und KI-Agent gleichzeitig:
- **Sofort-Antwort-Box** = fuer den Menschen die schnelle Kauf-Antwort, fuer die KI das zitierbare Nugget (40 bis 60 Woerter, self-contained).
- **Vergleichstabelle** (echte HTML-table, nie Bild) = Entscheidungshilfe und maschinenlesbare Rangliste.
- **Ehrlicher Nein-Pfad** ("Welches NICHT kaufen") = Vertrauen fuer den Menschen und Neutralitaets-Signal, das ueber Zitiert-werden entscheidet.
- **Praxis-Hinweis** (die 150-Watt-Falle im California) = der Nicht-Datenblatt-Layer, den generischer KI-Content nicht hat. Das ist der Helpful-Content-Unterscheider.
- **Kaufknopf immer NACH der Begruendung**, nie davor. Der Mehrwert traegt den Verkauf.

Schema-Markup (JSON-LD) steht statisch im `<head>` jeder Seite, nicht per JS nachgeladen, weil KI-Crawler oft kein JavaScript rendern.

## Affiliate-Links: was du tun musst

Die Link-Logik ist fertig. Du musst nur deine echten IDs eintragen, an EINER Stelle: oben in `vanlife-config.js`.

1. **Awin Publisher-Account anlegen** (schaltet EcoFlow, Anker Solix, Fritz Berger, Trelino, Boxio, Snooze frei). Dann `AWIN_ID` eintragen.
2. **Webgains Publisher-Account anlegen** (schaltet Bluetti, Offgridtec frei). Dann `WG_CAMPAIGN` eintragen.
3. **Amazon PartnerNet** (nur Fallback fuer Kleinkram). Dann `AMZN_TAG` eintragen.
4. Bei den Programmen, die du brauchst, einzeln bewerben (Freigabe dauert teils 1 bis 3 Tage). Merchant-IDs stehen bereits in `vanlife-config.js` unter `MERCHANTS` (vor Live verifizieren).

Sobald die IDs drin sind, bauen alle Buttons auf allen Seiten automatisch die richtigen Tracking-Links, setzen `rel="sponsored nofollow"`, `target="_blank"` und die Werbe-Kennzeichnung.

### Erste Programme (Prioritaet, aus dem Blueprint)

Sofort: Awin-Account, Anker Solix DE (Awin, 7-10 %, 30 Tage), EcoFlow DE (Awin, 5-8 %, 7 Tage), Webgains-Account, Bluetti EU (Webgains, bis 8 %, 30 Tage), Offgridtec (Webgains, 5 %), Amazon PartnerNet (Fallback).
Bald: Fritz Berger (Awin, Vollsortiment-Joker), Snooze Project (fuer Silo Schlafen).

## Wichtig: das ist ein ENTWURF

- Produkt- und Preisdaten sind **Beispielwerte** (als Range, mit Stand-Datum). Vor Live gegen Hersteller-Specs pruefen.
- Marke "VanKompass" ist ein **Arbeitstitel**.
- Merchant-IDs aus dem Blueprint vor Live verifizieren.
- Nur der Strom-Silo ist gebaut. Andere Kacheln zeigen auf "#".

## Naechste Schritte (laut Blueprint, in dieser Reihenfolge)

1. Programme anmelden (Awin, Webgains, Amazon) - das ist Markus' echte Hebelarbeit, nicht Schreiben.
2. Diesen einen Silo end-to-end fertig machen: Autark-Check-Tool bauen (aus dem Tool-Bauplan), Pillar + 10 Produkte + die ersten Money-Artikel.
3. 2 bis 3 Wochen Daten ziehen, ob Mensch UND KI anbeissen.
4. Erst dann auf die anderen 15 Silos skalieren (entlang der Modell-Achse) und spaeter den Mechanismus auf E-Bike kopieren.
5. Daten-Backbone: `affiliate-daten.xlsx` um Sheets `Silos`, `Modelle` erweitern, `build.py` um `read_silos`/`read_modelle` ergaenzen, damit die KI nur Daten pflegt und das Template eingefroren bleibt.

Vollstaendiger Blueprint, Tool-Specs, Richtlinie und Framework: siehe `../nischen-recherche/` und `../RICHTLINIE-phantom-affiliate-nischenseiten.md`.
