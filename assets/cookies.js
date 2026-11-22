// Aviso de cookies y Google Analytics 4.
// GA4 solo se carga si la persona pulsa «Aceptar». Si rechaza o no elige, no se carga nada de Google.
// La elección se guarda en este navegador (localStorage) y se puede cambiar desde el pie: «Preferencias de cookies».
(function () {
  var GA_ID = document.documentElement.getAttribute("data-ga");
  if (!GA_ID) return;
  var CLAVE = "el-director-cookies";
  var aviso = document.getElementById("aviso-cookies");

  function leer() { try { return localStorage.getItem(CLAVE); } catch (e) { return null; } }
  function guardar(v) { try { localStorage.setItem(CLAVE, v); } catch (e) {} }

  var cargado = false;
  function cargarAnalytics() {
    if (cargado) return;
    cargado = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag("js", new Date());
    window.gtag("config", GA_ID);
    var s = document.createElement("script");
    s.async = true;
    s.src = "https://www.googletagmanager.com/gtag/js?id=" + encodeURIComponent(GA_ID);
    document.head.appendChild(s);
  }
  function borrarCookiesGA() {
    document.cookie.split(";").forEach(function (c) {
      var n = c.split("=")[0].trim();
      if (n.indexOf("_ga") === 0) {
        var dom = location.hostname.replace(/^www\./, "");
        document.cookie = n + "=; Max-Age=0; path=/";
        document.cookie = n + "=; Max-Age=0; path=/; domain=." + dom;
      }
    });
  }
  function mostrar() { if (aviso) { aviso.hidden = false; var b = aviso.querySelector("button"); if (b) b.focus({ preventScroll: true }); } }
  function ocultar() { if (aviso) aviso.hidden = true; }

  if (aviso) {
    aviso.querySelector("[data-cookies=si]").addEventListener("click", function () { guardar("si"); ocultar(); cargarAnalytics(); });
    aviso.querySelector("[data-cookies=no]").addEventListener("click", function () {
      var antes = leer();
      guardar("no"); ocultar(); borrarCookiesGA();
      if (antes === "si") location.reload();   // descarga Analytics de la página actual
    });
  }
  document.querySelectorAll("[data-abrir-cookies]").forEach(function (b) {
    b.addEventListener("click", function (e) { e.preventDefault(); mostrar(); });
  });

  var eleccion = leer();
  if (eleccion === "si") cargarAnalytics();
  else if (eleccion !== "no") mostrar();
})();
