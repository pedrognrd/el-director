// Slider "Vida real, libro y película": cambia cada 5 s, pausa al pasar el ratón o con el foco,
// y no avanza solo si la persona prefiere reducir el movimiento.
(function () {
  var raiz = document.querySelector(".vrlp");
  if (!raiz) return;
  var slides = raiz.querySelectorAll(".vrlp-slide");
  var puntos = raiz.querySelectorAll(".vrlp-punto");
  var pausa = raiz.querySelector(".vrlp-pausa");
  var cta = raiz.querySelector(".vrlp-titulo a");
  var reducir = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var actual = 0, temporizador = null, pausado = reducir, encima = false;
  raiz.classList.add("js");

  function mostrar(n) {
    actual = (n + slides.length) % slides.length;
    slides.forEach(function (s, i) {
      var activa = i === actual;
      s.classList.toggle("activa", activa);
      s.setAttribute("aria-hidden", activa ? "false" : "true");
      s.querySelectorAll("a").forEach(function (a) { a.tabIndex = activa ? 0 : -1; });
    });
    puntos.forEach(function (p, i) { p.setAttribute("aria-current", i === actual ? "true" : "false"); });
    raiz.setAttribute("data-tono", slides[actual].getAttribute("data-tono") || "");
    var ultimo = actual === slides.length - 1;
    raiz.classList.toggle("ultimo", ultimo);
    cta.tabIndex = ultimo ? 0 : -1;
    programar();
  }
  function programar() {
    clearTimeout(temporizador);
    if (!pausado && !encima) temporizador = setTimeout(function () { mostrar(actual + 1); }, 5000);
  }
  function fijarPausa(v) {
    pausado = v;
    pausa.setAttribute("aria-label", v ? "Reanudar" : "Pausar");
    pausa.textContent = v ? "▶" : "❚❚";
    programar();
  }
  puntos.forEach(function (p, i) { p.addEventListener("click", function () { mostrar(i); }); });
  pausa.addEventListener("click", function () { fijarPausa(!pausado); });
  raiz.addEventListener("mouseenter", function () { encima = true; programar(); });
  raiz.addEventListener("mouseleave", function () { encima = false; programar(); });
  raiz.addEventListener("focusin", function () { encima = true; programar(); });
  raiz.addEventListener("focusout", function () { encima = false; programar(); });
  document.addEventListener("visibilitychange", function () { if (!document.hidden) programar(); else clearTimeout(temporizador); });
  fijarPausa(pausado);
  mostrar(0);
})();
