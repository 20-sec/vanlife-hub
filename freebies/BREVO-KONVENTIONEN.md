# Brevo-Konventionen fuer die VanKompass-Freebies

Verbindliches Schema, damit alle 16 Freebie-Strecken in Brevo gleich laufen. (Die QA hatte uneinheitliche Merge-Felder und Listennamen gefunden, das ist hier aufgeloest.)

## 1. Eine Liste, Segmentierung ueber ein Attribut

- **Eine Master-Liste:** `VanKompass Newsletter`.
- **Segmentierung ueber Kontakt-Attribut** `BEREICH` (Typ Text), Wert = Silo-Slug (`strom`, `schlafen`, `sanitaer` ...). Das Anmeldeformular jedes Bereichs setzt `BEREICH` automatisch (verstecktes Feld).
- **Reporting-Tag** (Brevo-Kategorie) je Anmeldung: `freebie-<silo>` (z.B. `freebie-strom`). Lowercase, einheitlich.

So bleibt es eine Liste (eine Abmeldung, keine Dubletten), aber sauber nach Interesse segmentiert. Spaetere Kauf-Mails koennen exakt einen Bereich ansprechen.

## 2. Ein Merge-Feld fuer die Anrede

- **Verbindlich:** `{{contact.VORNAME}}` (Brevo-Standardattribut in DE-Konten).
- **Fallback** bei leerem Vornamen: Anrede neutral, z.B. Mail-Einstieg `Hallo,` statt `Hallo {{contact.VORNAME}},`. In Brevo ueber Bedingung/Default loesen.
- Keine anderen Varianten verwenden (nicht FNAME, FIRSTNAME, contact.FNAME usw.).

## 3. Auslieferungs-Ablauf (DSGVO-konform, Double-Opt-in)

1. Nutzer fuellt das Bereichs-Formular aus (Vorname + E-Mail, verstecktes `BEREICH`).
2. Brevo sendet die **DOI-Bestaetigungsmail**. Darin steht KEIN Download-Link (erst nach bestaetigtem Opt-in).
3. Nach Klick auf den Bestaetigungslink startet eine **Automation** (Trigger: Kontakt bestaetigt in Liste `VanKompass Newsletter`).
4. Die **Willkommensmail** liefert den **Download-Link** zum PDF des passenden Bereichs (Logik nach Attribut `BEREICH`).
5. Optional: Danke-Seite mit direktem Download, falls die Mail im Spam landet.

## 4. PDF-Hosting

- PDF wird **als verlinkte Datei** ausgeliefert (nicht als Anhang). Besser fuer Zustellbarkeit und Klick-Tracking.
- Ablage entweder in Brevo unter Medien oder gehostet auf der VanKompass-Domain.
- **Gating-Hinweis fuer Live:** Im Entwurf liegen die PDFs offen unter `freebies/pdf/`. Sobald echt monetarisiert wird, die PDFs hinter einen schwer erratbaren Pfad legen oder ueber Brevo-Medien ausliefern und NICHT oeffentlich verlinken, sonst umgeht der Nutzer die E-Mail-Anmeldung.

## 5. Datei- und Pfad-Konvention (technisch)

- Freebie-Slug = Silo-Slug. PDF: `freebie-<silo>.pdf`. HTML-Quelle: `freebie-<silo>.html`.
- Modell-Hubs (z.B. VW California) tragen kein Freebie, also auch keine Liste/kein Tag.
