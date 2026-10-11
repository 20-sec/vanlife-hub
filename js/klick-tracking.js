(function () {
  // Klicks an GA4 melden, die die "optimierte Analyse" von selbst NICHT zaehlt:
  // interne Links, Sprungmarken, Buttons, E-Mail- und Telefonlinks. Ausgehende Links laesst
  // dieses Script bewusst liegen — die zaehlt GA4 bereits selbst, sonst stuende
  // jeder solche Klick doppelt im Report.
  //
  // Ohne Cookie-Zustimmung gibt es kein window.gtag. Dann passiert hier nichts:
  // die Zustimmung entscheidet, nicht dieses Script.
  function melde(name, ziel, text) {
    if (typeof window.gtag !== 'function') return;
    window.gtag('event', name, {
      // link_url und link_text sind GA4 als Dimensionen bereits bekannt —
      // deshalb genau diese Namen, sonst muesste man in GA4 von Hand
      // benutzerdefinierte Dimensionen anlegen.
      link_url:  String(ziel || '').substring(0, 100),
      link_text: String(text || '').replace(/\s+/g, ' ').trim().substring(0, 100)
    });
  }

  document.addEventListener('click', function (e) {
    var start = e.target;
    if (!start || !start.closest) return;
    var el = start.closest('a, button, [role="button"]');
    if (!el) return;

    var href = el.getAttribute('href') || '';
    var text = el.innerText || el.textContent || el.getAttribute('aria-label') || '';

    if (/^mailto:/i.test(href)) { melde('klick_mail', href.replace(/^mailto:/i, ''), text); return; }
    if (/^tel:/i.test(href))    { melde('klick_telefon', href.replace(/^tel:/i, ''), text); return; }

    if (el.tagName === 'A') {
      if (!href) return;

      // Sprungmarken. Auf Einseiten-Verkaufsseiten sind sie der eigentliche
      // Handlungsaufruf ("Jetzt kaufen" fuehrt auf #kauf, nicht auf eine
      // andere Seite). Draussen bleiben das leere "#" und die Sprunglinks
      // zum Seitenanfang, die es nur fuer die Tastaturbedienung gibt.
      if (href.charAt(0) === '#') {
        var ziel = href.slice(1).toLowerCase();
        if (!ziel || ['main', 'content', 'inhalt', 'top', 'seitenanfang', 'skip'].indexOf(ziel) !== -1) return;
        melde('klick_sprungmarke', href, text);
        return;
      }

      var url;
      try { url = new URL(href, location.href); } catch (_) { return; }
      if (url.protocol !== 'http:' && url.protocol !== 'https:') return;
      if (url.host !== location.host) return;             // ausgehend — zaehlt GA4 selbst
      // Anker mitnehmen: "/#kontakt" von einer Unterseite ist etwas anderes
      // als ein Link auf die Startseite. Ohne den Anker faellt beides auf "/"
      // zusammen und der Report zeigt nicht, welcher Handlungsaufruf gezogen hat.
      melde('klick_intern', url.pathname + url.search + url.hash, text);
      return;
    }

    // Menue-Knoepfe zaehlen nicht. Ein Klick auf den Hamburger sagt nur
    // "kam vom Handy", nicht "hat Interesse" — er wuerde die Button-Tabelle
    // im Report anfuehren und die aussagekraeftigen Knoepfe verdraengen.
    var kennung = ((el.getAttribute('class') || '') + ' ' + (el.id || '') + ' ' +
                   (el.getAttribute('aria-label') || '')).toLowerCase();
    if (/nav-?toggle|menu-?toggle|hamburger|burger|men[uü]/.test(kennung)) return;

    // Reine Symbol-Knoepfe (Pfeile, Kreuze) ebenso: ohne Buchstaben oder
    // Ziffern steht spaeter nichts Lesbares im Report.
    if (!/[a-z0-9äöüß]/i.test(text)) return;

    // Button ohne Ziel: als Ort gilt die Seite, auf der geklickt wurde —
    // welcher Button es war, steht in der Beschriftung.
    if (text.trim()) melde('klick_button', location.pathname, text);
  }, true);
})();
