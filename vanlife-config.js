/* ============================================================
   VanKompass (Arbeitstitel) - Zentrale Affiliate-Konfiguration
   ============================================================
   DIE EINE PFLEGESTELLE. Hier - und nur hier - traegst du deine
   echten IDs ein, sobald die Programme freigeschaltet sind.
   Jeder Kaufknopf auf jeder Seite baut seinen Link aus diesen Werten.
   Tag-Wechsel = eine Zeile, nicht 600 Artikel anfassen.

   Spaeter wandert dieser Block ins zentrale Affiliate-System
   (data.json -> affiliate_config), damit build.py ihn rendert.
   Fuer den Entwurf reicht diese Datei.
   ============================================================ */

window.VANLIFE_AFFILIATE = {
  // ---- HIER ECHTE IDs EINTRAGEN (aktuell Platzhalter) ----
  AWIN_ID:      "DEINE-AWIN-PUBLISHER-ID",   // Awin Publisher-Account (schaltet EcoFlow, Anker Solix, Fritz Berger, Trelino, Boxio, Snooze)
  AMZN_TAG:     "DEIN-AMAZON-TAG-21",        // Amazon PartnerNet Tracking-ID, nur Fallback fuer Kleinkram
  WG_CAMPAIGN:  "DEINE-WEBGAINS-CAMPAIGN",   // Webgains (schaltet Bluetti, Offgridtec)
  WG_CLICKREF:  "vankompass",                // freies Tracking-Label fuer Webgains

  // ---- Merchant-IDs der Programme (laut Blueprint, vor Live verifizieren) ----
  MERCHANTS: {
    "anker-solix": { netz: "awin",    mid: "32623", satz: "7-10 %", cookie: "30 Tage" },
    "ecoflow":     { netz: "awin",    mid: "51793", satz: "5-8 %",  cookie: "7 Tage"  },
    "bluetti":     { netz: "webgains", mid: "294040", satz: "bis 8 %", cookie: "30 Tage" },
    "offgridtec":  { netz: "webgains", mid: "12421",  satz: "5 %",    cookie: "30 Tage" },
    "fritz-berger":{ netz: "awin",    mid: "70949", satz: "5 %",    cookie: "30 Tage" }
  },

  // Pflicht-Kennzeichnung direkt am Knopf (UWG Paragraf 5a Abs. 4)
  kennzeichnung_text: "Werbung"
};

/* ------------------------------------------------------------
   resolveAffiliateLinks(): laeuft beim Laden, baut aus den
   data-* Attributen jedes .aff-btn den fertigen href, setzt
   rel="sponsored nofollow", target="_blank" und die Werbe-Kennzeichnung.

   Markup-Konvention pro Button:
     <a class="aff-btn primary"
        data-merchant="anker-solix"        (Direktprogramm-Schluessel ODER "amazon")
        data-target="https://...produkt"    (Ziel-URL beim Haendler)
        data-asin="B0XXXX"                  (nur bei data-merchant="amazon")
        data-label="Anker Solix C300 bei Anker ansehen">…</a>
   ------------------------------------------------------------ */
(function () {
  var C = window.VANLIFE_AFFILIATE;

  function buildHref(btn) {
    var merchant = btn.getAttribute("data-merchant");
    var target = btn.getAttribute("data-target") || "";
    if (merchant === "amazon") {
      var asin = btn.getAttribute("data-asin") || "";
      return "https://www.amazon.de/dp/" + asin + "/?tag=" + encodeURIComponent(C.AMZN_TAG);
    }
    var m = C.MERCHANTS[merchant];
    if (!m) return target || "#";
    if (m.netz === "awin") {
      return "https://www.awin1.com/cread.php?awinmid=" + m.mid +
             "&awinaffid=" + encodeURIComponent(C.AWIN_ID) +
             "&ued=" + encodeURIComponent(target);
    }
    if (m.netz === "webgains") {
      return "https://track.webgains.com/click.html?wgcampaignid=" + encodeURIComponent(C.WG_CAMPAIGN) +
             "&wgprogramid=" + m.mid +
             "&clickref=" + encodeURIComponent(C.WG_CLICKREF) +
             "&wgtarget=" + encodeURIComponent(target);
    }
    return target || "#";
  }

  function init() {
    var btns = document.querySelectorAll("a.aff-btn");
    for (var i = 0; i < btns.length; i++) {
      var b = btns[i];
      b.setAttribute("href", buildHref(b));
      b.setAttribute("rel", "sponsored nofollow");
      b.setAttribute("target", "_blank");
      // Werbe-Kennzeichnung direkt am Knopf, falls noch nicht im Markup
      if (!b.querySelector(".ad")) {
        var ad = document.createElement("span");
        ad.className = "ad";
        ad.textContent = "* " + C.kennzeichnung_text;
        b.appendChild(ad);
      }
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
