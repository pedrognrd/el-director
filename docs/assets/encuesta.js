// Encuesta "¿Quién es quién?": emparejar un personaje de la película con uno del libro.
// Dos modos:
// · PRUEBA (sin clave de Supabase): los votos se guardan solo en este navegador (localStorage).
// · REAL (con data-supabase-url y data-supabase-key): cada voto se envía a Supabase y los porcentajes
//   salen de la función resultados(), que solo devuelve recuentos. En el navegador solo se recuerda
//   qué personajes has votado ya, para no votar dos veces el mismo.
(function () {
  var raiz = document.getElementById("encuesta");
  if (!raiz) return;
  var datos = JSON.parse(document.getElementById("encuesta-datos").textContent);
  var base = raiz.getAttribute("data-base");
  var CLAVE = "el-director-encuesta-prueba-v1";
  var memoria = { votos: [] };
  var SB_URL = raiz.getAttribute("data-supabase-url"), SB_KEY = raiz.getAttribute("data-supabase-key");
  var REAL = !!(SB_URL && SB_KEY);
  if (REAL) CLAVE = "el-director-encuesta-v1";
  var remotos = [];   // [{peli, libro, votos}] desde Supabase
  function cabeceras() {
    var h = { "apikey": SB_KEY, "Content-Type": "application/json" };
    if (SB_KEY.indexOf("eyJ") === 0) h["Authorization"] = "Bearer " + SB_KEY;
    return h;
  }
  function cargarRemotos() {
    if (!REAL) return Promise.resolve();
    return fetch(SB_URL + "/rest/v1/rpc/resultados", { method: "POST", headers: cabeceras(), body: "{}" })
      .then(function (r) { if (!r.ok) throw new Error(r.status); return r.json(); })
      .then(function (d) { remotos = d || []; })
      .catch(function () { vivo.textContent = "No se han podido cargar los resultados."; });
  }
  function enviar(peli, libro) {
    if (!REAL) return Promise.resolve(true);
    var h = cabeceras(); h["Prefer"] = "return=minimal";
    return fetch(SB_URL + "/rest/v1/votos", { method: "POST", headers: h, body: JSON.stringify({ peli: peli, libro: libro }) })
      .then(function (r) { return r.ok; }).catch(function () { return false; });
  }

  var almacen = {
    cargar: function () {
      try { var v = JSON.parse(localStorage.getItem(CLAVE)); if (v && v.votos) memoria = v; } catch (e) {}
      return memoria.votos;
    },
    guardar: function () { try { localStorage.setItem(CLAVE, JSON.stringify(memoria)); } catch (e) {} },
    votar: function (peli, libro, propio) {
      if (propio) memoria.votos = memoria.votos.filter(function (v) { return !(v.propio && v.peli === peli); });
      memoria.votos.push({ peli: peli, libro: libro, propio: !!propio, t: Date.now() });
      this.guardar();
    },
    borrar: function () { memoria = { votos: [] }; this.guardar(); }
  };
  almacen.cargar();

  var porId = function (lista) { var m = {}; lista.forEach(function (x) { m[x.id] = x; }); return m; };
  var PELI = porId(datos.peli), LIBRO = porId(datos.libro);
  var esc = function (t) { return String(t).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); };
  var paso = raiz.querySelector(".enc-paso");
  var vivo = raiz.querySelector(".enc-vivo");

  function miVoto(peli) {
    for (var i = memoria.votos.length - 1; i >= 0; i--) { var v = memoria.votos[i]; if (v.propio && v.peli === peli) return v.libro; }
    return null;
  }
  function foto(p, clase) {
    return p.foto ? '<img class="' + clase + '" src="' + base + p.foto + '" alt="" width="300" height="300" loading="lazy" decoding="async">'
                  : '<img class="' + clase + ' sin-foto" src="' + base + 'assets/img/' + (p.sexo === "m" ? "silueta-mujer.png" : "silueta-hombre.png") + '" alt="" width="300" height="300" loading="lazy">';
  }
  function enfocar(sel) { var h = raiz.querySelector(sel); if (h) { h.setAttribute("tabindex", "-1"); h.focus({ preventScroll: true }); raiz.scrollIntoView({ behavior: "smooth", block: "start" }); } }

  function paso1() {
    paso.innerHTML = '<h2 class="enc-titulo">1. Elige un personaje de la película</h2>' +
      '<ul class="enc-rejilla">' + datos.peli.map(function (p) {
        var v = miVoto(p.id);
        return '<li><button type="button" class="enc-carta' + (v ? " votada" : "") + '" data-peli="' + p.id + '">' + foto(p, "enc-img") +
          '<span class="enc-nombre">' + esc(p.nombre) + '</span><span class="enc-sub">' + esc(p.actor) + '</span>' +
          (v ? '<span class="enc-marca">Tu voto: ' + esc(LIBRO[v].nombre) + '</span>' : "") + '</button></li>';
      }).join("") + '</ul>';
  }
  function paso2(idPeli) {
    var p = PELI[idPeli];
    var opciones = datos.libro.filter(function (l) { return l.sexo === p.sexo || l.sexo === "?" || l.sexo === "*"; });
    paso.innerHTML = '<button type="button" class="enc-volver">← Cambiar de personaje</button>' +
      '<div class="enc-elegido">' + foto(p, "enc-img-peq") + '<div><p class="antetitulo">Personaje de la película</p><h2 class="enc-titulo">' + esc(p.nombre) + '</h2><p class="enc-sub">' + esc(p.actor) + '</p></div></div>' +
      '<h3 class="enc-pregunta">2. ¿Qué personaje del libro crees que es?</h3>' +
      '<ul class="enc-rejilla libro">' + opciones.map(function (l) {
        return '<li><button type="button" class="enc-carta' + (l.tipo === "ninguno" ? " ninguno" : "") + '" data-libro="' + l.id + '">' + foto(l, "enc-img" + (l.tipo === "real" ? " real" : "")) +
          '<span class="enc-tipo ' + l.tipo + '">' + (l.tipo === "real" ? "Nombre real" : l.tipo === "apodo" ? "Apodo del libro" : "Opción") + '</span>' +
          '<span class="enc-nombre">' + esc(l.nombre) + '</span><span class="enc-sub">' + esc(l.desc) + '</span></button></li>';
      }).join("") + '</ul>';
    paso.setAttribute("data-peli", idPeli);
    enfocar(".enc-titulo");
  }
  function recuento(idPeli) {
    var c = {}, n = 0;
    if (REAL) remotos.forEach(function (v) { if (v.peli === idPeli) { c[v.libro] = (c[v.libro] || 0) + Number(v.votos); n += Number(v.votos); } });
    else memoria.votos.forEach(function (v) { if (v.peli === idPeli) { c[v.libro] = (c[v.libro] || 0) + 1; n++; } });
    var filas = Object.keys(c).map(function (k) { return { id: k, n: c[k], pct: Math.round(c[k] * 1000 / n) / 10 }; });
    filas.sort(function (a, b) { return b.n - a.n; });
    return { n: n, filas: filas };
  }
  function barras(idPeli, marcar) {
    var r = recuento(idPeli);
    if (!r.n) return '<p class="enc-sub">Aún no hay votos.</p>';
    return '<ol class="enc-barras">' + r.filas.map(function (f) {
      return '<li class="' + (f.id === marcar ? "tuya" : "") + '"><span class="enc-barra-nombre">' + esc(LIBRO[f.id].nombre) + (f.id === marcar ? " · tu voto" : "") + '</span>' +
        '<span class="enc-barra"><span style="width:' + f.pct + '%"></span></span><span class="enc-pct">' + String(f.pct).replace(".", ",") + ' %</span></li>';
    }).join("") + '</ol><p class="enc-sub">' + r.n + (r.n === 1 ? " voto" : " votos") + '</p>';
  }
  function paso3(idPeli, idLibro, yaVotado) {
    var p = PELI[idPeli], l = LIBRO[idLibro];
    paso.innerHTML = '<p class="antetitulo">' + (yaVotado ? "Ya votaste este personaje" : "Tu respuesta") + '</p><h2 class="enc-titulo">' + esc(p.nombre) + ' = ' + esc(l.nombre) + '</h2>' +
      '<p class="enc-sub">Así han respondido sobre ' + esc(p.nombre) + ' (' + esc(p.actor) + '):</p>' + barras(idPeli, idLibro) +
      '<div class="flechas"><button type="button" class="enc-otro">Emparejar otro personaje</button></div>' +
      '<p class="enc-invita">¿Quieres saber más de cada personaje? La historia completa está en el libro y en la película.</p>' +
      '<div class="flechas"><a href="' + base + 'libro/#donde-leer">Dónde leer el libro</a><a href="' + base + 'pelicula/#donde-ver">Dónde ver la película</a></div>';
    enfocar(".enc-titulo");
    vivo.textContent = "Voto registrado: " + p.nombre + " con " + l.nombre + ".";
    resumen();
  }
  function resumen() {
    var caja = document.getElementById("encuesta-resultados");
    if (!caja) return;
    var conVotos = datos.peli.filter(function (p) { return recuento(p.id).n; });
    caja.innerHTML = conVotos.length ? '<ul class="enc-resumen">' + conVotos.map(function (p) {
      return '<li>' + foto(p, "enc-img-peq") + '<div><h3>' + esc(p.nombre) + ' <span class="enc-sub">' + esc(p.actor) + '</span></h3>' + barras(p.id, miVoto(p.id)) + '</div></li>';
    }).join("") + '</ul>' : '<p class="enc-sub">Todavía no hay votos. Empieza por elegir un personaje.</p>';
  }

  raiz.addEventListener("click", function (e) {
    var b = e.target.closest("button");
    if (!b) return;
    if (b.dataset.peli) {
      var ya = miVoto(b.dataset.peli);
      // En modo real solo se vota una vez por personaje: si ya votaste, se muestran los resultados.
      if (REAL && ya) { cargarRemotos().then(function () { paso3(b.dataset.peli, ya, true); }); }
      else paso2(b.dataset.peli);
    }
    else if (b.dataset.libro) {
      var idp = paso.getAttribute("data-peli"), idl = b.dataset.libro;
      b.disabled = true;
      enviar(idp, idl).then(function (ok) {
        if (!ok) { b.disabled = false; vivo.textContent = "No se ha podido guardar el voto. Inténtalo de nuevo."; alert("No se ha podido guardar el voto. Inténtalo de nuevo."); return; }
        almacen.votar(idp, idl, true);
        if (window.gtag) window.gtag("event", "voto_encuesta", { personaje_pelicula: idp, personaje_libro: idl });
        return cargarRemotos().then(function () { paso3(idp, idl); });
      });
    }
    else if (b.classList.contains("enc-volver") || b.classList.contains("enc-otro")) { paso1(); enfocar(".enc-titulo"); }
  });
  var simular = document.getElementById("enc-simular"), borrar = document.getElementById("enc-borrar");
  if (simular) simular.addEventListener("click", function () {
    for (var i = 0; i < 50; i++) {
      var p = datos.peli[Math.floor(Math.random() * datos.peli.length)];
      var ops = datos.libro.filter(function (l) { return l.sexo === p.sexo || l.sexo === "?" || l.sexo === "*"; });
      // sesgo para que los porcentajes no salgan planos
      var l = ops[Math.floor(Math.pow(Math.random(), 2.2) * ops.length)];
      almacen.votar(p.id, l.id, false);
    }
    vivo.textContent = "Añadidos 50 votos simulados."; resumen(); paso1();
  });
  if (borrar) borrar.addEventListener("click", function () { almacen.borrar(); vivo.textContent = "Votos de prueba borrados."; resumen(); paso1(); });
  paso1(); resumen();
  if (REAL) cargarRemotos().then(resumen);
})();
