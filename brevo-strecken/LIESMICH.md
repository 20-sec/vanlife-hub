# VanKompass Brevo-Strecken

Vollständiger Baukasten, mit dem du die 16 Freebie-Newsletter-Strecken in Brevo in kurzer Zeit händisch aufsetzt. **Einmal verstehen, 16x mechanisch durchziehen.**

## Was hier liegt

| Datei | Zweck |
|---|---|
| `uebersicht.html` | Startseite mit allen Links: Anleitung, DOI-Mail, 16 Strecken |
| `anleitung.html` | Die einmalige Erklärung: Architektur + Setup + Vorgehen |
| `ANLEITUNG.pdf` | Dieselbe Anleitung als PDF (im VanKompass-CI), zum Mitnehmen aufs Tablet |
| `strecke-doi.html` | Die globale DOI-Mail (gilt für alle 16, einmal in Brevo hinterlegen) |
| `strecke-<silo>.html` (16x) | Pro Bereich ein Baukasten mit allen kopierbaren Bausteinen: Formular-Konfig, Welcome-Mail-Betreff, Preheader, vollständiges Mail-HTML, Live-Vorschau, Automation-Konfig |
| `build-mails.py` | Generator (Vanilla Python). Liest `../freebies/freebies-data.json` und rendert alles. Mit `--pdf` zusätzlich die PDF-Anleitung |

## Architektur (so hängt es zusammen)

- **1 Liste** in Brevo: *VanKompass Newsletter* (alle 16 Strecken schreiben hier rein)
- **1 Kontakt-Attribut** *BEREICH*: Wert = Silo-Slug (`strom`, `schlafen`, ...). Damit entscheidet die Automation, wer welches Freebie bekommt
- **1 globale DOI-Mail**, einmal hinterlegt
- **Pro Bereich**: 1 Formular + 1 Welcome-Mail-Template + 1 Automation. Identische Mechanik, nur Inhalte und der BEREICH-Filter ändern sich

## Vorgehen

1. **Einmal lesen:** `anleitung.html` oder `ANLEITUNG.pdf` (ca. 5 Minuten)
2. **Einmal in Brevo:** Liste anlegen, Attribut anlegen, DOI-Mail einrichten, Absender-Domain authentifizieren (ca. 20 Minuten)
3. **Eine Strecke testen:** Empfehlung Strom. Welcome-Mail-Template + Formular + Automation. Mit eigener Mail testen, ob alles ankommt
4. **Die restlichen 15** in einem Schwung, je ca. 10 Minuten. Pro Strecke öffnest du `strecke-<silo>.html`, kopierst die Bausteine in Brevo, fertig

## Was ich am Mail-Design beachtet habe

- **Mail-safe HTML:** Tabellen-Layout, Inline-Styles, keine externen CSS-Dateien. Funktioniert in allen gängigen Mail-Clients (Gmail, Apple Mail, Outlook, Web-Clients)
- **Mobile-freundlich:** max-width 600, responsive über Viewport-Meta
- **Pflicht-Footer:** Abmelde-Link (`{{unsubscribe}}`), Impressum-/Datenschutz-Verweis, Begründung der Mail (DSGVO Art. 13)
- **Personalisierung:** `{{contact.VORNAME}}` mit neutralem Verhalten bei leerem Feld
- **VanKompass-CI:** Petrol-Header, Amber-Knopf, dezenter Tipp-Block, gleiche Familie wie die PDFs

## Wenn du noch etwas brauchst

- **Andere Welcome-Mail-Texte?** Ändere `welcome_body()` in `build-mails.py`, dann `python3 build-mails.py --pdf` → alle 16 sind neu
- **Andere DOI-Mail?** Ändere `doi_body()` in `build-mails.py`, dann neu bauen
- **Neuer Bereich?** Ergänze `freebies-data.json`, dann neu bauen, der Baukasten entsteht automatisch
- **Eigene Schreibstimme?** Die Mails sind aktuell in der neutralen VanKompass-Redaktions-Stimme. Wenn du persönlicher willst (Markus' Stimme), sag Bescheid

## Strategischer Hinweis

Brevo-Strecken einzurichten ist eine **einmalige Aufgabe**, die du an einem Vormittag durchziehst. Nicht spannend, aber die Voraussetzung, dass die Freebies überhaupt ihren Job tun. Während du das machst, kann parallel der Strom-Cluster ausgebaut werden (Tool + Landingpage + Money-Artikel). Das hängt nicht voneinander ab.
