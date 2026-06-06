# VOR LIVE PRÜFEN — VanKompass

Diese Liste muss abgearbeitet sein, bevor noindex/robots.txt gelöst und die Seite öffentlich freigegeben wird. Sie ist absichtlich pessimistisch geschrieben, weil im Live-Modus jeder Fehler Vertrauen kostet.

Stand: 2026-06-06. Owner: Markus.

---

## A. Produkt-Fact-Check (HÖCHSTE PRIORITÄT)

Die Money-Artikel und das Tool nennen konkrete Produkte mit Preisen. Beispieldaten aus KI-Recherche, **nicht händisch verifiziert**. Vor Live: jedes Produkt prüfen.

### Strom-Cluster Produkte zu verifizieren

- [ ] **Anker Solix C300** (in California, Ford Nugget): existiert? Preis 250-320 €? Kapazität ~288 Wh, ~300 W, Reinsinus?
- [ ] **EcoFlow River 3 Plus** (in California, Ford Nugget): existiert? Preis 300-430 €? Erweiterbar mit Zusatzakku?
- [ ] **EcoFlow Delta 3 Plus** (in Ford Nugget Tool): existiert in dieser Bezeichnung? Preis 600-750 €? Kapazität ~1024 Wh?
- [ ] **Bluetti AC180** (in allen drei Artikeln): existiert, Preis 600-800 €, 1152 Wh, 1800 W Dauerleistung? Ja, Bluetti AC180 ist real.
- [ ] **Offgridtec LiFePO4 100Ah** (Kastenwagen, Tool): exakter Produktname? Preis 400-550 €? Bei welchem Händler kaufbar?
- [ ] **LiTime 100Ah Smart** (Kastenwagen): existiert? Bluetooth-App? Preis 350-450 €?
- [ ] **Anker Solix F2000 mit Hausanschluss-Kit** (Kastenwagen): existiert ein solches "Hausanschluss-Kit" wirklich? Oder erfunden?
- [ ] **Victron Orion-Tr Smart 12/12-30** (Kastenwagen): existiert, ~200 €?
- [ ] **Fritz Berger LiFePO4-Set** (im Tool): exakte Produktbezeichnung?
- [ ] **Victron SmartShunt** (im California-Artikel erwähnt): existiert, korrekter Name?

### Praxis-Hinweise zu verifizieren

- [ ] **VW California 150-W-Steckdose ohne Reinsinus**: stimmt das? Modelle T5/T6/T6.1/T7? Quelle Westfalia-Datenblatt prüfen.
- [ ] **Ford Nugget Aufstelldach Stauraum unter Sitzbank**: passt eine Anker Solix C300 (B×T×H ca. 30×17×22 cm) wirklich rein?
- [ ] **Standheizung-Anlaufstrom ~200 W Spitze**: stimmt das fachlich?
- [ ] **Ducato/Sprinter ab 2018 smarte Lichtmaschine**: ab welchem Modelljahr genau? Welche Motoren?
- [ ] **LiFePO4 unter 0°C nicht laden**: korrekt, gut belegen.

### Hersteller-Affiliate-Programme verifizieren

Im Brevo-Baukasten und in vanlife-config.js stehen Merchant-IDs aus dem Recherche-Blueprint. Vor Live prüfen:

- [ ] **Anker Solix DE Awin merchant 32623**: Existiert das so? Aktueller Provisionssatz? Cookie-Dauer?
- [ ] **EcoFlow DE Awin merchant 51793**: Existiert? Aktuelle Konditionen?
- [ ] **Bluetti EU Webgains merchant 294040**: Existiert?
- [ ] **Offgridtec Webgains merchant 12421**: Existiert?
- [ ] **Fritz Berger Awin merchant 70949**: Existiert?

---

## B. Schema-Markup / SEO

- [x] AggregateRating in allen Product-Schemas entfernt (Kastenwagen-Artikel war betroffen, gefixt 2026-06-06)
- [ ] **JSON-LD validieren** mit Google Rich Results Test für jede produktive Seite
- [ ] **Article-Schema Publisher logo.url** ergänzen sobald Logo-URL feststeht
- [ ] **Person-Schema für Autor "Jan Berger"**: Wer ist das? Echter Autor oder Pseudonym? Bei Pseudonym Impressum klären, ob das DSGVO-konform ist
- [ ] **OG/Twitter-Cards**: aktuell nicht gesetzt, für Social-Sharing ergänzen
- [ ] **Canonical-Tags**: aktuell nicht gesetzt, vor Live einbauen
- [ ] **Sitemap.xml** generieren und in Search Console einreichen

---

## C. Affiliate-Infrastruktur

- [x] Hybrid-Resolver gefixt (MutationObserver, idempotent, funktioniert auch bei reaktivem Re-Render)
- [ ] **Echte IDs in vanlife-config-v2.js eintragen**: AWIN_ID, AMZN_TAG, WG_CAMPAIGN
- [ ] **Pflicht-Snippet Amazon-PartnerNet**: "Als Amazon-Partner verdiene ich an qualifizierten Verkäufen" — steht im Footer, aber prüfen ob exakter Wortlaut PartnerNet-konform
- [ ] **Beispiel-ASINs ersetzen**: `B0EXAMPLE01`, `B0EXAMPLE02` usw. durch echte ASINs
- [ ] **Beispiel-Target-URLs ersetzen**: vereinzelt sind Hersteller-URLs Platzhalter
- [ ] **Affiliate-Link-Verwaltung**: einmal entscheiden, ob die echten Links in `affiliate-daten.xlsx` (bestehendes System) gepflegt werden und per build.py rausgeschrieben, oder direkt in vanlife-config-v2.js. Empfehlung: über Excel pflegen für Konsistenz mit den anderen Phantom-Schiffen.

---

## D. Mobile

- [ ] **Tool auf 375 px Viewport testen**: Slider, Checkboxen, Ergebnis-Box bedienbar?
- [ ] **Money-Artikel auf 375 px**: Tabelle scrollt? Buttons treffbar?
- [ ] **Landingpage auf 375 px**: Form prominent? Vorschau lesbar?
- [ ] **Touch-Targets**: alle Buttons mindestens 44×44 px?

---

## E. Conversion-Pfade

- [ ] **Brevo-Strecken** komplett eingerichtet (16 Strecken, siehe brevo-strecken/)
- [ ] **Freebie-PDFs** ins Brevo-Medien-Verzeichnis hochgeladen oder hinter geschützten URLs ablegen (sonst umgehen Nutzer die Anmeldung)
- [ ] **Test-Anmeldung** für jede der 16 Strecken einmal durchspielen: DOI-Mail kommt, bestätigen, PDF kommt
- [ ] **CTA-Konsistenz**: jede Money-Seite hat den Freebie-CTA an der richtigen Stelle (sekundär, nach dem Fazit)
- [ ] **Tool-Funnel**: Tool → Produktempfehlung → Klick → Tracking?

---

## F. Hub-Architektur Vollständigkeit

Aktuell ist nur der Strom-Silo gebaut. Vor Live entscheiden:
- [ ] Geht VanKompass mit **nur Strom-Silo** plus Hub live, mit Hinweis "weitere Bereiche folgen"?
- [ ] Oder Live erst, wenn **2-3 Silos** komplett sind?
- [ ] Modell-Hubs (`/camper/vw-california/` etc.) noch nicht gebaut. Vor Live?

---

## G. Inhaltliche Konsistenz

- [x] Echte Umlaute (ä ö ü ß) in allen Hub-Dateien und Cluster-Inhalten verifiziert
- [x] Keine Gedankenstriche im Fließtext
- [ ] **Autor-Bio "Jan Berger"** vereinheitlichen: aktuell "Redakteur VanKompass, Selbstausbauer". Mit Markus klären ob das so bleibt
- [ ] **Stand-Datum überall**: Juni 2026 konsistent? Bei späterem Live-Gang aktualisieren
- [ ] **Proto-Banner** (`<div class="proto-banner">...`) vor Live entfernen!
- [ ] **noindex/nofollow** vor Live entfernen (alle HTML-Dateien)
- [ ] **robots.txt** vor Live durch echte Version ersetzen (mit Sitemap-Verweis und freigegebenen KI-Crawlern)

---

## H. Rechtliches

- [ ] **Impressum** mit rc:com UG-Angaben befüllen
- [ ] **Datenschutzerklärung** mit Brevo als Auftragsverarbeiter, Affiliate-Cookies, Hosting (GitHub Pages oder spätere Domain)
- [ ] **Cookie-Banner** entscheiden: erforderlich? Wenn ja, vor Live einbauen
- [ ] **Affiliate-Disclosure** auf jeder Seite mit Affiliate-Links vorhanden (ist drin, prüfen ob Wortlaut UWG-konform)
- [ ] **HMW** (Health Marketing Werbung) und Heilmittelwerbegesetz: für Strom-Silo nicht relevant

---

## Reihenfolge

1. Brevo aufsetzen (Markus parallel, läuft schon)
2. A. Produkt-Fact-Check (zeitintensiv, aber unverzichtbar)
3. C. Echte Affiliate-IDs eintragen
4. E. Brevo-Test-Anmeldungen je Strecke
5. D. Mobile-Pass
6. B. Schema-Validierung
7. G. Proto-Banner, noindex und robots.txt entfernen
8. H. Rechtliches final
9. F. Architektur-Entscheidung (Strom-only oder mehrere Silos)
10. Go live

---

## Was JETZT bereits sicher ist (Stand 2026-06-06)

- ✅ Tool-Berechnung funktional verifiziert (Verbraucher anhaken → Tagesbedarf, Speicher, Architektur, Produktempfehlungen springen reaktiv)
- ✅ Hybrid-Affiliate-Resolver funktioniert bei reaktiv gerenderten Buttons (MutationObserver)
- ✅ Schema-Markup ohne erfundene Ratings
- ✅ Echte Umlaute durchgängig
- ✅ Keine Gedankenstriche
- ✅ noindex überall, robots.txt sperrt komplett
- ✅ Money-Artikel-Template trägt (3 Artikel gebaut)
- ✅ Brevo-Baukasten komplett (16 Strecken plus DOI plus Anleitung)
- ✅ 16 Freebie-PDFs gerendert
