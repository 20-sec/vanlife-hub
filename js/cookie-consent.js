(function () {
  var STORAGE_KEY = 'ts_cookie_consent';
  // Mess-ID der rc:com-Property (Umzug 02.09.2026). Vorher lief hier
  // G-G5SXQQCTV3 aus dem 20sec-Konto — die Property bleibt dort mit ihrer
  // Historie liegen, misst aber ab dem Domain-Transfer nichts mehr.
  var GA4_ID = 'G-3MENXQ8XF2';
  function loadGA4(){ if(window._ga4Loaded)return; window._ga4Loaded=true;
    var s=document.createElement('script'); s.async=true;
    s.src='https://www.googletagmanager.com/gtag/js?id='+GA4_ID; document.head.appendChild(s);
    window.dataLayer=window.dataLayer||[]; window.gtag=function(){dataLayer.push(arguments);};
    gtag('js',new Date()); gtag('config',GA4_ID); }
  function hide(){var b=document.getElementById('ts-cookie-banner'); if(b)b.style.display='none';}
  function show(){var b=document.getElementById('ts-cookie-banner'); if(b)b.style.display='flex';}
  window.tsAcceptCookies=function(){localStorage.setItem(STORAGE_KEY,'accepted');hide();loadGA4();};
  window.tsDeclineCookies=function(){localStorage.setItem(STORAGE_KEY,'declined');hide();};
  window.tsShowCookieBanner=function(){localStorage.removeItem(STORAGE_KEY);show();};
  var v=localStorage.getItem(STORAGE_KEY);
  if(v==='accepted'){loadGA4();} else if(!v){document.addEventListener('DOMContentLoaded',show);}
})();
