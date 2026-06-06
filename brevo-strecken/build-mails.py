#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VanKompass Brevo-Strecken-Generator.

Baut aus freebies-data.json fuer jeden der 16 Bereiche EIN Baukasten-HTML
mit allen kopierbaren Bausteinen, die Markus in Brevo einsetzt:
  - Welcome-Mail Subject
  - Welcome-Mail Preheader
  - Welcome-Mail HTML-Body (mail-safe, inline-Styles, mobile-tauglich)
  - Formular-Konfig (Liste, Attribut-Wert, Erfolgsmeldung)
  - Automation-Konfig (Trigger, Bedingung, Aktion)

Plus eine globale DOI-Mail (gilt fuer alle 16, einmal in Brevo hinterlegen).
Plus eine Uebersichts-Seite mit Links zu allen 16 Baukaesten.
Plus ein PDF der Anleitung via Chrome --print-to-pdf.

Aufruf:
  python3 build-mails.py          # nur HTML
  python3 build-mails.py --pdf    # zusaetzlich PDF der Anleitung
"""
import json, os, sys, html, subprocess, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(os.path.dirname(HERE), "freebies", "freebies-data.json")

SILO_NAME = {
    "cockpit": "Cockpit", "strom": "Batterie & Strom", "solar": "Solar",
    "schlafen": "Schlafen", "sanitaer": "Toilette & Sanitär", "kueche": "Küche",
    "wasser": "Wasser", "heizung": "Heizung", "verdunkelung": "Verdunkelung & Insektenschutz",
    "stauraum": "Stauraum", "aussenbereich": "Außenbereich", "sicherheit": "Sicherheit",
    "internet": "Internet", "apps": "Camper-Apps", "sitze": "Sitze & Drehkonsole", "sound": "Sound",
}

# ---------- Mail-Body (mail-safe, inline-Styles) ----------

PETROL = "#0f3d3e"
AMBER = "#e08a2b"
AMBER_DARK = "#c4751c"
SAND = "#f4ead7"
INK = "#1c2321"
MUTED = "#5d6b66"
LINE = "#d9d2c2"


def esc(s):
    return html.escape(s or "", quote=True)


def mail_shell(title, preheader, body_inner):
    """Liefert ein vollstaendiges Mail-HTML. Inline-Styles, table-basiert,
    fuer alle gaengigen Mail-Clients tauglich."""
    return f"""<!DOCTYPE html>
<html lang="de"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
</head><body style="margin:0;padding:0;background:#f0eadb;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif;color:{INK};">
<div style="display:none;max-height:0;overflow:hidden;opacity:0;font-size:1px;line-height:1px;color:#f0eadb;">{esc(preheader)}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:#f0eadb;">
  <tr><td align="center" style="padding:24px 12px;">
    <table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" style="max-width:600px;width:100%;background:#ffffff;border-radius:14px;overflow:hidden;box-shadow:0 4px 16px rgba(15,61,62,.08);">
      <tr><td style="background:{PETROL};color:#ffffff;padding:18px 26px;font-weight:800;font-size:18px;letter-spacing:-.3px;">
        <span style="display:inline-block;width:24px;height:24px;border-radius:6px;background:{AMBER};color:{PETROL};text-align:center;line-height:24px;font-weight:900;vertical-align:middle;margin-right:8px;">V</span>
        VanKompass
      </td></tr>
      <tr><td style="padding:26px 28px 8px;font-size:16px;line-height:1.55;color:{INK};">
        {body_inner}
      </td></tr>
      <tr><td style="padding:18px 28px 26px;color:{MUTED};font-size:12px;line-height:1.6;border-top:1px solid {LINE};">
        Du erhältst diese Mail, weil du dich auf vankompass.de für ein kostenloses Freebie angemeldet hast.<br>
        VanKompass &middot; rc:com UG (haftungsbeschränkt) &middot; <a href="{{{{unsubscribe}}}}" style="color:{MUTED};">Newsletter abbestellen</a> &middot; <a href="https://vankompass.de/datenschutz/" style="color:{MUTED};">Datenschutz</a> &middot; <a href="https://vankompass.de/impressum/" style="color:{MUTED};">Impressum</a>
      </td></tr>
    </table>
  </td></tr>
</table>
</body></html>"""


def welcome_body(fb):
    title = fb["freebieTitle"]
    silo_name = SILO_NAME.get(fb["siloSlug"], fb["siloSlug"])
    pdf = f"https://vankompass.de/freebies/freebie-{fb['siloSlug']}.pdf"
    return f"""
<p style="margin:0 0 14px;font-size:18px;color:{PETROL};font-weight:700;">Hallo {{{{contact.VORNAME}}}},</p>
<p style="margin:0 0 14px;">danke, dass du dabei bist. Wie versprochen, hier ist deine {esc(title.split(':')[0])}:</p>

<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="margin:18px 0 22px;">
  <tr><td style="background:{AMBER};border-radius:10px;">
    <a href="{pdf}" style="display:inline-block;padding:14px 28px;color:{PETROL};text-decoration:none;font-weight:700;font-size:16px;">PDF herunterladen</a>
  </td></tr>
</table>

<p style="margin:0 0 14px;">{esc(fb.get('coverHook',''))}</p>

<p style="margin:18px 0 6px;font-weight:700;color:{PETROL};">Was dich von uns künftig erwartet</p>
<p style="margin:0 0 14px;">Wir schicken dir etwa einmal pro Woche eine ehrliche Empfehlung zum Thema {esc(silo_name)} und manchmal einen Hinweis auf etwas Neues bei VanKompass. Keine Verkaufstaktiken, kein Spam. Wenn du es nicht mehr willst, am Ende jeder Mail ein Klick zum Abmelden.</p>

<p style="margin:22px 0 14px;">Wenn du Fragen hast, antworte einfach auf diese Mail.<br>Viele Grüße von der Insel,<br><strong>die VanKompass-Redaktion</strong></p>

<p style="margin:22px 0 0;padding:12px 14px;background:{SAND};border-radius:8px;font-size:14px;color:{INK};">
  <strong>Tipp:</strong> Speicher dir diese Mail. Du kannst das PDF jederzeit über den Link oben erneut laden.
</p>
"""


def doi_body():
    """Globale DOI-Bestaetigungsmail. Gilt fuer alle 16 Strecken."""
    return f"""
<p style="margin:0 0 14px;font-size:18px;color:{PETROL};font-weight:700;">Hallo {{{{contact.VORNAME}}}},</p>
<p style="margin:0 0 14px;">eine kurze Bestätigung noch, damit wir sicher sind, dass du das warst: Bitte klicke auf den Knopf unten, dann schicken wir dir deinen Download direkt im nächsten Schritt.</p>

<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="margin:18px 0 22px;">
  <tr><td style="background:{AMBER};border-radius:10px;">
    <a href="{{{{doubleoptin}}}}" style="display:inline-block;padding:14px 28px;color:{PETROL};text-decoration:none;font-weight:700;font-size:16px;">Anmeldung bestätigen</a>
  </td></tr>
</table>

<p style="margin:0 0 14px;color:{MUTED};font-size:14px;">Wenn der Knopf nicht funktioniert, kopiere bitte diesen Link in deinen Browser:<br><span style="color:{PETROL};">{{{{doubleoptin}}}}</span></p>

<p style="margin:18px 0 0;">Falls du diese Mail nicht angefordert hast, ignoriere sie einfach. Ohne deine Bestätigung passiert nichts.</p>

<p style="margin:22px 0 0;">Viele Grüße,<br><strong>die VanKompass-Redaktion</strong></p>
"""


# ---------- Baukasten-Seite pro Bereich ----------

PAGE_STYLES = f"""
:root {{ --petrol:{PETROL}; --amber:{AMBER}; --amber-d:{AMBER_DARK}; --sand:{SAND}; --ink:{INK}; --muted:{MUTED}; --line:{LINE}; }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--sand); color:var(--ink); font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif; line-height:1.55; }}
.wrap {{ max-width:980px; margin:0 auto; padding:24px 20px 60px; }}
.cover {{ background:var(--petrol); color:#fff; padding:22px 26px; border-radius:14px 14px 0 0; display:flex; align-items:center; gap:10px; }}
.cover .mark {{ width:26px; height:26px; border-radius:7px; background:var(--amber); color:var(--petrol); display:inline-grid; place-items:center; font-weight:900; }}
.cover .kind {{ margin-left:auto; background:var(--amber); color:var(--petrol); font-weight:700; font-size:11pt; padding:5px 12px; border-radius:999px; }}
.card {{ background:#fff; padding:26px 28px; border-radius:0 0 14px 14px; box-shadow:0 4px 18px rgba(15,61,62,.08); }}
h1 {{ font-size:24pt; color:var(--petrol); margin:18px 0 6px; letter-spacing:-.3px; }}
h2 {{ font-size:14pt; color:var(--petrol); margin:24px 0 10px; padding-bottom:6px; border-bottom:2px solid var(--sand); }}
h3 {{ font-size:11.5pt; color:var(--petrol); margin:18px 0 6px; }}
p {{ margin:0 0 10px; }}
.field {{ background:var(--sand); padding:10px 14px; border-radius:8px; margin:6px 0; font-family:'SF Mono','Menlo','Monaco',monospace; font-size:11pt; }}
.field strong {{ color:var(--petrol); font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; }}
.copy {{ position:relative; }}
.copy textarea {{ width:100%; min-height:140px; padding:14px 16px; border:1px solid var(--line); border-radius:10px; font-family:'SF Mono','Menlo','Monaco',monospace; font-size:10.5pt; line-height:1.5; background:#fafafa; resize:vertical; }}
.copy button {{ position:absolute; top:8px; right:8px; background:var(--petrol); color:#fff; border:none; padding:8px 14px; border-radius:8px; font-weight:600; cursor:pointer; font-size:11pt; }}
.copy button:hover {{ background:#0a2c2d; }}
.copy button.ok {{ background:#2e7d52; }}
.note {{ background:#fff7e9; border-left:4px solid var(--amber); padding:10px 14px; border-radius:0 8px 8px 0; margin:14px 0; font-size:10.5pt; }}
.steps {{ counter-reset:step; padding:0; margin:0; list-style:none; }}
.steps li {{ counter-increment:step; padding:10px 0 10px 38px; position:relative; border-bottom:1px dashed var(--line); }}
.steps li:last-child {{ border-bottom:none; }}
.steps li::before {{ content:counter(step); position:absolute; left:0; top:8px; width:26px; height:26px; border-radius:50%; background:var(--petrol); color:#fff; font-weight:800; text-align:center; line-height:26px; font-size:13px; }}
.preview {{ border:1px solid var(--line); border-radius:10px; overflow:hidden; margin:8px 0 4px; max-height:480px; }}
.preview iframe {{ width:100%; height:480px; border:0; }}
.toc {{ display:grid; grid-template-columns:repeat(2,1fr); gap:10px; margin:18px 0; }}
@media (max-width:680px) {{ .toc {{ grid-template-columns:1fr; }} }}
.toc a {{ background:#fff; border:1px solid var(--line); padding:12px 14px; border-radius:10px; text-decoration:none; color:var(--ink); display:block; }}
.toc a:hover {{ border-color:var(--amber); }}
.toc a strong {{ display:block; color:var(--petrol); font-size:13pt; margin-bottom:2px; }}
.toc a span {{ color:var(--muted); font-size:11pt; }}
.btn-back {{ display:inline-block; color:var(--petrol); text-decoration:none; font-weight:600; margin:0 0 10px; }}
@page {{ size:A4; margin:14mm; }}
@media print {{ body {{ background:#fff; }} .copy button {{ display:none; }} }}
"""

COPY_JS = """
<script>
function cp(btn){
  const ta = btn.parentElement.querySelector('textarea');
  ta.select();
  ta.setSelectionRange(0, 99999);
  try { navigator.clipboard.writeText(ta.value); } catch(e) { document.execCommand('copy'); }
  const old = btn.textContent;
  btn.textContent = 'Kopiert.';
  btn.classList.add('ok');
  setTimeout(() => { btn.textContent = old; btn.classList.remove('ok'); }, 1600);
}
</script>
"""


def baukasten_page(fb, idx, total):
    silo = fb["siloSlug"]
    silo_name = SILO_NAME.get(silo, silo)
    title = fb["freebieTitle"]
    short_title = title.split(":")[0]

    welcome_subject = f"Da ist deine {short_title}"
    welcome_preheader = fb.get("coverHook", "")[:120]
    welcome_html = mail_shell(welcome_subject, welcome_preheader, welcome_body(fb))

    form_success = f"Danke. Schau in dein E-Mail-Postfach: dort wartet eine kurze Bestätigungsmail von uns. Klick den Knopf darin, dann bekommst du dein PDF."

    return f"""<!DOCTYPE html>
<html lang="de"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Brevo-Baukasten {idx}/{total}: {esc(silo_name)} | VanKompass</title>
<style>{PAGE_STYLES}</style>
</head><body>
<div class="wrap">
  <a class="btn-back" href="uebersicht.html">&larr; Zur Übersicht aller 16 Strecken</a>
  <div class="cover">
    <span class="mark">V</span>
    <div><strong>VanKompass Brevo-Baukasten</strong><br><span style="font-size:11pt;opacity:.85;">Strecke {idx} von {total}</span></div>
    <div class="kind">{esc(silo_name)}</div>
  </div>
  <div class="card">
    <h1>{esc(short_title)}</h1>
    <p style="color:var(--muted);">Alle Bausteine, die du in Brevo einsetzt, fertig zum Kopieren. Folge der <a href="anleitung.html" style="color:var(--amber-d);font-weight:600;">Anleitung</a> und arbeite die Strecke in einem Rutsch durch.</p>

    <h2>1. Formular (Brevo &rarr; Formulare &rarr; Neues Formular)</h2>
    <div class="field"><strong>Liste:</strong> VanKompass Newsletter</div>
    <div class="field"><strong>Pflichtfelder:</strong> VORNAME, E-Mail</div>
    <div class="field"><strong>Verstecktes Feld BEREICH (vorbelegt):</strong> {silo}</div>
    <div class="field"><strong>Double-Opt-in:</strong> aktiviert (Pflicht)</div>

    <h3>Erfolgsmeldung nach Absenden</h3>
    <div class="copy">
      <button onclick="cp(this)">Kopieren</button>
      <textarea readonly>{esc(form_success)}</textarea>
    </div>

    <h2>2. Welcome-Mail Template (Brevo &rarr; Vorlagen &rarr; Neue Vorlage &rarr; HTML)</h2>
    <h3>Betreff</h3>
    <div class="copy">
      <button onclick="cp(this)">Kopieren</button>
      <textarea readonly style="min-height:50px;">{esc(welcome_subject)}</textarea>
    </div>

    <h3>Preheader / Vorschau-Text</h3>
    <div class="copy">
      <button onclick="cp(this)">Kopieren</button>
      <textarea readonly style="min-height:60px;">{esc(welcome_preheader)}</textarea>
    </div>

    <h3>Mail-HTML (vollstaendig, fertig zum Einfuegen in Brevo HTML-Editor)</h3>
    <div class="copy">
      <button onclick="cp(this)">Kopieren</button>
      <textarea readonly>{esc(welcome_html)}</textarea>
    </div>

    <h3>Vorschau</h3>
    <div class="preview"><iframe srcdoc="{esc(welcome_html)}" title="Vorschau {esc(silo_name)}"></iframe></div>

    <h2>3. Automation (Brevo &rarr; Automation &rarr; Neuer Workflow)</h2>
    <div class="field"><strong>Workflow-Name:</strong> Freebie {silo_name} ausliefern</div>
    <div class="field"><strong>Trigger:</strong> Kontakt wird zur Liste &quot;VanKompass Newsletter&quot; hinzugefügt</div>
    <div class="field"><strong>Bedingung:</strong> Kontakt-Attribut BEREICH ist gleich &quot;{silo}&quot;</div>
    <div class="field"><strong>Aktion:</strong> Sende E-Mail &rarr; Vorlage &quot;Freebie {silo_name}&quot; (die du in Schritt 2 angelegt hast)</div>
    <div class="note">Wichtig: Brevo sendet die Welcome-Mail erst, NACHDEM der Kontakt die DOI-Bestätigung geklickt hat. Das ist der Standard-Schutz. Du musst dafür nichts extra konfigurieren, solange du oben Double-Opt-in aktiviert hast.</div>

    <h2>Check: Was ist nach dieser Strecke fertig?</h2>
    <ul class="steps">
      <li>Formular für {esc(silo_name)} steht und schreibt in die Liste &quot;VanKompass Newsletter&quot; mit BEREICH={silo}.</li>
      <li>Welcome-Mail-Template &quot;Freebie {esc(silo_name)}&quot; ist angelegt.</li>
      <li>Automation &quot;Freebie {esc(silo_name)} ausliefern&quot; ist aktiv.</li>
      <li>Test mit deiner eigenen E-Mail durchgeführt: DOI-Mail kommt &rarr; bestätigt &rarr; Welcome-Mail mit Download-Link kommt &rarr; PDF lädt.</li>
    </ul>
  </div>
</div>
{COPY_JS}
</body></html>"""


def doi_page():
    subject = "Bitte bestätige kurz deine Anmeldung"
    preheader = "Ein Klick, dann schicken wir dir dein Freebie."
    doi_html = mail_shell(subject, preheader, doi_body())

    return f"""<!DOCTYPE html>
<html lang="de"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>Globale DOI-Mail | VanKompass Brevo-Baukasten</title>
<style>{PAGE_STYLES}</style>
</head><body>
<div class="wrap">
  <a class="btn-back" href="uebersicht.html">&larr; Zur Übersicht</a>
  <div class="cover">
    <span class="mark">V</span>
    <div><strong>VanKompass Brevo-Baukasten</strong><br><span style="font-size:11pt;opacity:.85;">Einmalig für alle 16 Strecken</span></div>
    <div class="kind">DOI-Mail</div>
  </div>
  <div class="card">
    <h1>Die globale DOI-Mail</h1>
    <p style="color:var(--muted);">Diese Mail bekommt jeder, der sich anmeldet, BEVOR er das Freebie erhält. Sie ist für alle 16 Strecken dieselbe. Du legst sie einmal in Brevo als Standard-DOI-Mail fest.</p>

    <h2>Wo in Brevo?</h2>
    <p>Brevo &rarr; Kontakte &rarr; Einstellungen &rarr; Double-Opt-in-Bestätigungsmail. Dort trägst du Betreff und HTML ein. Das Token <code style="background:var(--sand);padding:1px 6px;border-radius:4px;">{{{{doubleoptin}}}}</code> ersetzt Brevo automatisch durch den individuellen Bestätigungs-Link.</p>

    <h2>Betreff</h2>
    <div class="copy">
      <button onclick="cp(this)">Kopieren</button>
      <textarea readonly style="min-height:50px;">{esc(subject)}</textarea>
    </div>

    <h2>Preheader</h2>
    <div class="copy">
      <button onclick="cp(this)">Kopieren</button>
      <textarea readonly style="min-height:50px;">{esc(preheader)}</textarea>
    </div>

    <h2>Mail-HTML</h2>
    <div class="copy">
      <button onclick="cp(this)">Kopieren</button>
      <textarea readonly>{esc(doi_html)}</textarea>
    </div>

    <h2>Vorschau</h2>
    <div class="preview"><iframe srcdoc="{esc(doi_html)}" title="DOI-Mail Vorschau"></iframe></div>
  </div>
</div>
{COPY_JS}
</body></html>"""


def anleitung_page(freebies):
    cards = "\n".join(
        f'<a href="strecke-{fb["siloSlug"]}.html"><strong>{i+1}. {esc(SILO_NAME.get(fb["siloSlug"], fb["siloSlug"]))}</strong><span>{esc(fb["freebieTitle"].split(":")[0])}</span></a>'
        for i, fb in enumerate(freebies)
    )
    return f"""<!DOCTYPE html>
<html lang="de"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>So baust du die VanKompass-Brevo-Strecken | Anleitung</title>
<style>{PAGE_STYLES}</style>
</head><body>
<div class="wrap">
  <div class="cover">
    <span class="mark">V</span>
    <div><strong>VanKompass</strong><br><span style="font-size:11pt;opacity:.85;">Brevo-Strecken Anleitung</span></div>
    <div class="kind">einmal verstehen, 16x durchziehen</div>
  </div>
  <div class="card">
    <h1>So baust du die VanKompass-Brevo-Strecken</h1>
    <p style="color:var(--muted);font-size:12pt;">Diese Anleitung erklärt das Vorgehen einmal. Danach machst du für jeden der 16 Bereiche dasselbe, mit den fertigen Bausteinen aus dem jeweiligen Baukasten. Plane für die einmaligen Schritte ca. 20 Minuten, pro Strecke danach ca. 10 Minuten.</p>

    <h2>Die Architektur (so hängt es zusammen)</h2>
    <ul>
      <li>Eine Liste in Brevo: <strong>VanKompass Newsletter</strong>. Alle 16 Strecken schreiben in diese eine Liste.</li>
      <li>Ein Kontakt-Attribut <strong>BEREICH</strong>. Sein Wert (z.B. &quot;strom&quot;) entscheidet, welches Freebie der Abonnent bekommt und welcher Newsletter ihn später trifft.</li>
      <li>Eine globale DOI-Mail. Gilt für alle 16, einmal hinterlegt.</li>
      <li>Pro Bereich: ein Formular, ein Welcome-Mail-Template, eine Automation. Identische Mechanik, nur Inhalte und der BEREICH-Wert ändern sich.</li>
    </ul>

    <h2>A. Einmaliges Setup (machst du genau einmal)</h2>
    <ol class="steps">
      <li><strong>Absender-Domain authentifizieren.</strong> Brevo &rarr; Einstellungen &rarr; Absender und IP &rarr; Domains: vankompass.de hinzufügen und die SPF/DKIM-Einträge bei deinem Hoster eintragen. Ohne das landen die Mails im Spam.</li>
      <li><strong>Liste anlegen.</strong> Brevo &rarr; Kontakte &rarr; Listen &rarr; Neue Liste: <em>VanKompass Newsletter</em>.</li>
      <li><strong>Kontakt-Attribut anlegen.</strong> Brevo &rarr; Kontakte &rarr; Einstellungen &rarr; Kontakt-Attribute &rarr; Neues Attribut: Name <em>BEREICH</em>, Typ <em>Text</em>.</li>
      <li><strong>DOI-Mail einrichten.</strong> Brevo &rarr; Kontakte &rarr; Einstellungen &rarr; Double-Opt-in-Bestätigungsmail: Betreff und HTML aus dem <a href="strecke-doi.html" style="color:var(--amber-d);font-weight:600;">DOI-Baukasten</a> einsetzen.</li>
      <li><strong>Datenschutz.</strong> Prüfe, dass die VanKompass-Datenschutzerklärung Brevo als Auftragsverarbeiter nennt (Standard-Bausteine, hat Brevo selbst dokumentiert). Footer-Link in den Mails zeigt darauf.</li>
    </ol>

    <h2>B. Pro Strecke (16x dieselbe Mechanik)</h2>
    <p>Öffne den Baukasten für den jeweiligen Bereich (Liste unten). Dort findest du die kopierbaren Bausteine. Arbeite eine Strecke in einem Rutsch durch:</p>
    <ol class="steps">
      <li><strong>Welcome-Mail anlegen.</strong> Brevo &rarr; Kampagnen &rarr; Vorlagen &rarr; Neue Vorlage &rarr; HTML-Editor. Betreff und HTML aus dem Baukasten kopieren. Speichern als <em>Freebie [Bereich]</em>.</li>
      <li><strong>Formular bauen.</strong> Brevo &rarr; Kontakte &rarr; Formulare &rarr; Neues Formular. Felder VORNAME (Pflicht) und E-Mail. Verstecktes Feld <em>BEREICH</em> mit dem Wert aus dem Baukasten vorbelegen. Liste auswählen: VanKompass Newsletter. DOI aktivieren. Erfolgsmeldung aus dem Baukasten einsetzen. Embed-Code später in die Landingpage einbauen.</li>
      <li><strong>Automation anlegen.</strong> Brevo &rarr; Automation &rarr; Neuer Workflow. Trigger: Kontakt wird zur Liste hinzugefügt. Bedingung: BEREICH ist gleich dem Wert aus dem Baukasten. Aktion: Sende E-Mail mit der Vorlage aus Schritt 1.</li>
      <li><strong>PDF hochladen.</strong> Lade das passende Freebie-PDF in Brevo Medien hoch ODER lege es auf vankompass.de unter freebies/. Den Link trägt die Welcome-Mail bereits, du musst nichts ändern, solange die URL stimmt.</li>
      <li><strong>Testen.</strong> Mit einer Test-Adresse anmelden. DOI-Mail muss kommen, bestätigen, Welcome-Mail muss kommen, PDF muss laden. Erst dann zur nächsten Strecke.</li>
    </ol>

    <h2>C. Die 16 Strecken</h2>
    <div class="toc">{cards}</div>
    <p style="margin-top:18px;"><a href="strecke-doi.html" style="color:var(--amber-d);font-weight:600;">&rarr; Plus: die globale DOI-Mail (einmal für alle)</a></p>

    <h2>Hinweise und Fallstricke</h2>
    <ul>
      <li><strong>Personalisierung:</strong> Wir nutzen überall <code style="background:var(--sand);padding:1px 6px;border-radius:4px;">{{{{contact.VORNAME}}}}</code>. Wenn kein Vorname vorliegt, trägt Brevo eine leere Zeichenkette ein. Fällt nur leicht auf, ist tolerierbar.</li>
      <li><strong>Abmelde-Link:</strong> <code style="background:var(--sand);padding:1px 6px;border-radius:4px;">{{{{unsubscribe}}}}</code> ist im Footer drin, Brevo setzt den Link automatisch.</li>
      <li><strong>DOI-Link:</strong> <code style="background:var(--sand);padding:1px 6px;border-radius:4px;">{{{{doubleoptin}}}}</code> ist NUR in der globalen DOI-Mail zu setzen.</li>
      <li><strong>Welche Liste pro Formular?</strong> Immer dieselbe: VanKompass Newsletter. Die Segmentierung kommt über das Attribut BEREICH.</li>
      <li><strong>Reihenfolge:</strong> Starte mit der DOI-Mail und einer Strecke (Empfehlung: Strom), teste dort sauber durch. Erst danach die anderen 15. Dann hast du das System einmal verstanden und der Rest ist Routine.</li>
    </ul>
  </div>
</div>
{COPY_JS}
</body></html>"""


def uebersicht_page(freebies):
    cards = "\n".join(
        f'<a href="strecke-{fb["siloSlug"]}.html"><strong>{i+1}. {esc(SILO_NAME.get(fb["siloSlug"], fb["siloSlug"]))}</strong><span>{esc(fb["freebieTitle"].split(":")[0])}</span></a>'
        for i, fb in enumerate(freebies)
    )
    return f"""<!DOCTYPE html>
<html lang="de"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>VanKompass Brevo-Strecken Übersicht</title>
<style>{PAGE_STYLES}</style>
</head><body>
<div class="wrap">
  <div class="cover">
    <span class="mark">V</span>
    <div><strong>VanKompass</strong><br><span style="font-size:11pt;opacity:.85;">Brevo-Strecken</span></div>
    <div class="kind">Übersicht</div>
  </div>
  <div class="card">
    <h1>16 Strecken plus eine globale DOI-Mail</h1>
    <p style="color:var(--muted);font-size:12pt;">Starte mit der <a href="anleitung.html" style="color:var(--amber-d);font-weight:600;">Anleitung</a>. Dort steht das einmalige Setup. Pro Strecke folgst du dann dem jeweiligen Baukasten.</p>
    <div class="note">Empfohlene Reihenfolge: erst die globale DOI-Mail einrichten, dann eine Strecke (Strom) komplett durchziehen und testen, danach die restlichen 15 Strecken in einem Schwung. Pro Strecke ca. 10 Minuten. Tipp: Mach den Test mit deiner privaten Mail-Adresse, dann siehst du die echte Erfahrung des Abonnenten.</div>

    <h2>Globaler Baustein</h2>
    <div class="toc">
      <a href="anleitung.html"><strong>Die Anleitung</strong><span>Einmal verstehen, 16x durchziehen</span></a>
      <a href="strecke-doi.html"><strong>DOI-Mail (global)</strong><span>Einmalig für alle 16 hinterlegen</span></a>
    </div>

    <h2>Die 16 Strecken</h2>
    <div class="toc">{cards}</div>
  </div>
</div>
</body></html>"""


def make_pdf(src, out):
    chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    if not os.path.exists(chrome):
        print("Chrome nicht gefunden, ueberspringe PDF.")
        return False
    url = "file://" + urllib.request.pathname2url(src)
    try:
        subprocess.run([chrome, "--headless", "--disable-gpu", "--no-pdf-header-footer",
                        f"--print-to-pdf={out}", url], check=True, capture_output=True, timeout=60)
        return True
    except Exception as e:
        print(f"PDF-Fehler: {e}")
        return False


def main():
    with open(DATA, encoding="utf-8") as f:
        freebies = json.load(f)

    # Pro Bereich
    for i, fb in enumerate(freebies):
        out = os.path.join(HERE, f"strecke-{fb['siloSlug']}.html")
        with open(out, "w", encoding="utf-8") as o:
            o.write(baukasten_page(fb, i + 1, len(freebies)))

    # DOI-Mail
    with open(os.path.join(HERE, "strecke-doi.html"), "w", encoding="utf-8") as o:
        o.write(doi_page())

    # Anleitung + Uebersicht
    with open(os.path.join(HERE, "anleitung.html"), "w", encoding="utf-8") as o:
        o.write(anleitung_page(freebies))
    with open(os.path.join(HERE, "uebersicht.html"), "w", encoding="utf-8") as o:
        o.write(uebersicht_page(freebies))

    print(f"{len(freebies)} Baukasten-Seiten + DOI + Anleitung + Uebersicht erzeugt.")

    if "--pdf" in sys.argv:
        if make_pdf(os.path.join(HERE, "anleitung.html"), os.path.join(HERE, "ANLEITUNG.pdf")):
            print("  ANLEITUNG.pdf gerendert.")


if __name__ == "__main__":
    main()
