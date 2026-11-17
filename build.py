#!/usr/bin/env python3
"""Genera el sitio estático "El Director. Del libro a la película".

Uso:  python3 build.py [usuario-github] [repositorio]
Escribe los HTML en ./docs (carpeta que publica GitHub Pages).
"""
import json, os, sys, shutil, html

USUARIO = sys.argv[1] if len(sys.argv) > 1 else "pedrognrd"
REPO = sys.argv[2] if len(sys.argv) > 2 else "el-director"
SITE = f"https://{USUARIO.lower()}.github.io/{REPO}/"
ISSUES = f"https://github.com/{USUARIO}/{REPO}/issues/new"
ACTUALIZADO = "2026-11-17"
ACTUALIZADO_TXT = "17 de noviembre de 2026"
SALIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")

MENU = [
    ("personajes/", "Quién es quién"),
    ("libro/", "El libro"),
    ("pelicula/", "La película"),
    ("historia-real/", "Historia real"),
    ("preguntas-frecuentes/", "Preguntas"),
]

# ---------- Enlaces externos ----------
AMAZON = "https://amzn.eu/d/0aOE6Rxm"
TODOSTUSLIBROS = "https://www.todostuslibros.com/busquedas?keyword=9788417678081"
MARCIALPONS = "https://www.marcialpons.es/libros/el-director/9788417678081/"
LIBROSDELKO = "https://www.librosdelko.com/"
BETA = "https://betafiction.es/cine/el-director/"
TAQUILLA = "https://www.taquilla.com/entradas/el-director-2026"
YOUTUBE = "https://www.youtube.com/@DavidJimenezElDirector"

F = {
    "wiki_libro": ("Wikipedia: El director (libro)", "https://es.wikipedia.org/wiki/El_director"),
    "wiki_peli": ("Wikipedia: El director (película)", "https://es.wikipedia.org/wiki/El_director_(pel%C3%ADcula)"),
    "wiki_autor": ("Wikipedia: David Jiménez García", "https://es.wikipedia.org/wiki/David_Jim%C3%A9nez_Garc%C3%ADa"),
    "beta": ("Beta Fiction Spain: ficha oficial", BETA),
    "av451": ("Audiovisual451: estreno el 20 de noviembre", "https://www.audiovisual451.com/el-director-estreno-en-cines-20-de-noviembre/"),
    "infobae": ("Infobae: primer vistazo a El director (10/07/2026)", "https://www.infobae.com/espana/cultura/2026/07/10/primer-vistazo-a-el-director-la-pelicula-basada-en-el-exitoso-libro-de-david-jimenez-sobre-sus-experiencias-en-el-mundo/"),
    "cineconn": ("Cineconn: primer tráiler", "https://cineconn.es/dani-de-la-orden-el-director-david-jimenez-el-mundo/"),
    "cinemagavia": ("Cinemagavia: crítica", "https://cinemagavia.es/el-director-pelicula-critica-estreno-cine/"),
    "ecartelera": ("eCartelera: reparto", "https://www.ecartelera.com/peliculas/el-director/reparto/"),
    "coverkitchen": ("Cover Kitchen: diseño de la portada", "https://coverkitchen.squarespace.com/memoir/el-director"),
    "elsalto": ("El Salto: entrevista a David Jiménez", "https://www.elsaltodiario.com/medios/entrevista-david-jimenez-director-mundo-libro-acuerdos-prensa-empresas-ibex-cloacas-estado-informacion-falsa-podemos"),
    "youtube": ("YouTube: canal oficial de David Jiménez", YOUTUBE),
}

def fuentes(*claves):
    items = "".join(f'<li><a href="{F[k][1]}" rel="noopener">{F[k][0]}</a></li>' for k in claves)
    return f'<aside class="fuentes" aria-label="Fuentes"><p class="actualizado">Actualizado el {ACTUALIZADO_TXT}</p><p>Fuentes:</p><ul>{items}</ul><p>¿Ves un error? <a href="{{r}}metodologia-y-fuentes/#rectificaciones">Pide una rectificación</a>.</p></aside>'

def migas(*items):
    li = []
    for i, (txt, url) in enumerate(items):
        if url is None:
            li.append(f'<li aria-current="page">{txt}</li>')
        else:
            li.append(f'<li><a href="{{r}}{url}">{txt}</a></li>')
    return f'<nav class="migas" aria-label="Migas de pan"><ol>{"".join(li)}</ol></nav>'

def ld_migas(items):
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u}
            for i, (n, u) in enumerate(items)
        ],
    }

LIBRO_LD = {
    "@type": "Book", "@id": SITE + "libro/#libro",
    "name": "El director: secretos e intrigas de la prensa narrados por el exdirector de El Mundo",
    "author": {"@type": "Person", "@id": SITE + "personajes/david-jimenez/#persona", "name": "David Jiménez García"},
    "publisher": {"@type": "Organization", "name": "Libros del K.O."},
    "datePublished": "2019-04-08", "inLanguage": "es", "isbn": "9788417678081", "numberOfPages": 328,
    "genre": "No ficción",
}
PELI_LD = {
    "@type": "Movie", "@id": SITE + "pelicula/#pelicula", "name": "El director",
    "director": {"@type": "Person", "name": "Dani de la Orden"},
    "dateCreated": "2026", "datePublished": "2026-11-20", "inLanguage": "es", "countryOfOrigin": "ES",
    "genre": ["Thriller", "Drama"],
    "isBasedOn": {"@id": SITE + "libro/#libro"},
    "actor": [{"@type": "Person", "name": n} for n in [
        "David Verdaguer", "Alberto San Juan", "Fernando Colomo", "Xavi Sáez", "Miriam Iscla", "Joan Carreras",
        "Carmen Machi", "Emma Vilarasau", "Guillermo Toledo", "Fernando Cayo"]],
    "productionCompany": [{"@type": "Organization", "name": n} for n in [
        "Beta Fiction Spain", "Sábado Time", "Cardinal Content", "Historias de un Director SL"]],
}

def plantilla(ruta, titulo, descripcion, cuerpo, ld=None, activo=None, portada=False):
    profundidad = ruta.count("/")
    r = "../" * profundidad
    canonica = SITE + ruta
    actual = ' aria-current="page"'
    menu = "".join(
        f'<li><a href="{r}{u}"{actual if u == activo else ""}>{t}</a></li>' for u, t in MENU
    )
    grafo = {"@context": "https://schema.org", "@graph": [
        {"@type": "WebSite", "@id": SITE + "#web", "name": "El Director. Del libro a la película", "url": SITE, "inLanguage": "es"},
        {"@type": "WebPage", "@id": canonica, "url": canonica, "name": titulo, "description": descripcion,
         "isPartOf": {"@id": SITE + "#web"}, "dateModified": ACTUALIZADO, "inLanguage": "es"},
    ] + (ld or [])}
    cuerpo = cuerpo.replace("{r}", r)
    return f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{html.escape(titulo)}</title>
<meta name="description" content="{html.escape(descripcion)}">
<link rel="canonical" href="{canonica}">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta name="theme-color" content="#0f2a2c">
<meta property="og:type" content="website">
<meta property="og:locale" content="es_ES">
<meta property="og:site_name" content="El Director. Del libro a la película">
<meta property="og:title" content="{html.escape(titulo)}">
<meta property="og:description" content="{html.escape(descripcion)}">
<meta property="og:url" content="{canonica}">
<meta name="twitter:card" content="summary">
<link rel="icon" href="{r}assets/icono.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=UnifrakturCook:wght@700&family=Oswald:wght@400;500;600&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&family=IBM+Plex+Mono:wght@400;500&display=swap">
<link rel="stylesheet" href="{r}assets/estilos.css">
<script type="application/ld+json">{json.dumps(grafo, ensure_ascii=False)}</script>
</head>
<body>
<a class="salto" href="#contenido">Saltar al contenido</a>
<div class="cinta">Estreno en cines: 20 de noviembre de 2026 · <a href="{r}metodologia-y-fuentes/">Web informativa e independiente</a></div>
<header class="sitio">
  <div class="contenedor">
    <a class="marca" href="{r}"><span class="el">El</span> Director<small>Del libro a la película</small></a>
    <nav aria-label="Principal"><ul class="menu">{menu}</ul></nav>
  </div>
</header>
<main id="contenido"{' class="sin-relleno"' if portada else ''}>
{cuerpo}
</main>
<footer class="pie">
  <div class="contenedor">
    <div>
      <p><strong>Sobre esta web.</strong> “El Director. Del libro a la película” es un proyecto independiente con fines informativos. No es la web oficial del libro, de la película ni de su autor, y no está vinculado a Libros del K.O., Beta Fiction Spain ni David Jiménez.</p>
      <p>La relación entre personas reales y personajes se basa en fuentes públicas enlazadas en cada página, con su grado de certeza. No emitimos juicios sobre las personas mencionadas. La película es una obra de ficción inspirada en hechos reales.</p>
      <p><strong>Sin fines comerciales.</strong> Sin publicidad, sin enlaces de afiliado y sin cookies. Los enlaces a librerías y cines son solo informativos.</p>
    </div>
    <ul>
      <li><a href="{r}personajes/">Quién es quién</a></li>
      <li><a href="{r}libro/">El libro</a></li>
      <li><a href="{r}pelicula/">La película</a></li>
      <li><a href="{r}historia-real/">Historia real</a></li>
      <li><a href="{r}personajes/david-jimenez/">David Jiménez</a></li>
      <li><a href="{r}preguntas-frecuentes/">Preguntas frecuentes</a></li>
      <li><a href="{r}metodologia-y-fuentes/">Metodología, fuentes y aviso legal</a></li>
      <li><a href="{r}metodologia-y-fuentes/#rectificaciones">Rectificaciones</a></li>
    </ul>
  </div>
</footer>
</body>
</html>
"""

def siguiente(*items):
    a = "".join(f'<a href="{{r}}{u}"><span class="antetitulo">{e}</span><strong>{t}</strong></a>' for e, t, u in items)
    return f'<nav class="siguiente" aria-label="Sigue leyendo">{a}</nav>'

DONDE_LEER = f"""<div class="donde">
  <a class="btn" href="{AMAZON}" rel="noopener">Amazon</a>
  <a class="btn sec" href="{TODOSTUSLIBROS}" rel="noopener">Librerías independientes</a>
  <a class="btn sec" href="{MARCIALPONS}" rel="noopener">Marcial Pons</a>
  <a class="btn sec" href="{LIBROSDELKO}" rel="noopener">Libros del K.O.</a>
</div>"""
DONDE_VER = f"""<div class="donde">
  <a class="btn" href="{BETA}" rel="noopener">Ficha y entradas (Beta Fiction)</a>
  <a class="btn sec" href="{TAQUILLA}" rel="noopener">Taquilla.com</a>
</div>"""

PAGINAS = {}

# ---------------- PORTADA ----------------
PAGINAS[""] = dict(
    titulo="El Director: quién es quién del libro a la película",
    desc="Qué persona real hay detrás de cada personaje de El Director, el libro de David Jiménez y la película de Dani de la Orden. Con fuentes y grado de certeza.",
    cuerpo=f"""
<section class="portada" style="margin-top:-40px">
  <div class="contenedor">
    <p class="antetitulo">Libro de David Jiménez (2019) · Película de Dani de la Orden (2026)</p>
    <h1><span class="el">El</span> Director</h1>
    <p class="sub">Del libro a la película</p>
    <p class="entradilla lectura">En 2015, David Jiménez dejó de ser corresponsal de guerra para dirigir <i>El Mundo</i>. Duró un año. Lo contó en un libro con nombres reales y apodos; ahora llega al cine con los nombres cambiados. Aquí te contamos quién es quién.</p>
    <div class="acciones">
      <a class="btn" href="{{r}}personajes/">Ver quién es quién</a>
      <a class="btn sec" href="{{r}}pelicula/#donde-ver">Dónde ver la película</a>
      <a class="btn sec" href="{{r}}libro/#donde-leer">Dónde leer el libro</a>
    </div>
  </div>
</section>
<div class="contenedor">
  <h2>Vida real, libro y película</h2>
  <div class="pares">
    <a class="par" href="{{r}}personajes/cardenal/">
      <div><div class="eti">Vida real</div><div class="nombre">Antonio Fernández-Galiano</div><div class="detalle">En el libro: “El Cardenal”</div></div>
      <div class="igual" aria-hidden="true">=</div>
      <div class="der"><div class="eti">Película</div><div class="nombre">Cardenal</div><div class="detalle">Alberto San Juan</div></div>
    </a>
    <a class="par" href="{{r}}personajes/david-jimenez/">
      <div><div class="eti">Vida real</div><div class="nombre">David Jiménez</div><div class="detalle">En el libro: el narrador</div></div>
      <div class="igual" aria-hidden="true">=</div>
      <div class="der"><div class="eti">Película</div><div class="nombre">David Jiménez</div><div class="detalle">David Verdaguer</div></div>
    </a>
    <a class="par" href="{{r}}personajes/#pendientes">
      <div><div class="eti">En el libro</div><div class="nombre">La Digna, El Señorito, Rasputín…</div><div class="detalle">Apodos de periodistas y directivos</div></div>
      <div class="igual duda" aria-hidden="true">?</div>
      <div class="der"><div class="eti">Película</div><div class="nombre">Por confirmar</div><div class="detalle">Tras el estreno</div></div>
    </a>
  </div>
  <p class="nota">Solo mostramos como confirmadas las relaciones que publican el autor, la productora o varios medios. <a href="{{r}}metodologia-y-fuentes/">Cómo trabajamos</a>.</p>

  <div class="rejilla" style="margin-top:44px">
    <div class="tarjeta"><h3>El libro</h3><p><i>El director</i> (Libros del K.O., 2019) relata el año de Jiménez al frente de <i>El Mundo</i> y el sistema de pactos entre prensa, empresas y política que él llama “Los Acuerdos”.</p><p><a href="{{r}}libro/">Sobre el libro</a></p></div>
    <div class="tarjeta"><h3>La película</h3><p>Thriller de Dani de la Orden con David Verdaguer y Alberto San Juan. Llega a los cines el 20 de noviembre de 2026.</p><p><a href="{{r}}pelicula/">Ficha y reparto</a></p></div>
    <div class="tarjeta"><h3>La historia real</h3><p>Del despido de Pedro J. Ramírez a la salida de Jiménez en mayo de 2016: lo que pasó en el periódico, en orden.</p><p><a href="{{r}}historia-real/">Cronología</a></p></div>
  </div>
</div>
""",
    ld=[LIBRO_LD, PELI_LD], portada=True,
)

# ---------------- PERSONAJES ----------------
PAGINAS["personajes/"] = dict(
    titulo="Personajes reales de El Director: quién es quién",
    desc="Tabla de personajes de El Director: persona real, apodo en el libro de David Jiménez y personaje y actor en la película. Con fuentes y grado de certeza.",
    activo="personajes/",
    cuerpo=f"""<div class="contenedor">
{migas(("Inicio", ""), ("Quién es quién", None))}
<p class="antetitulo">Quién es quién</p>
<h1>Personajes reales de <span class="el">El</span> Director</h1>
<div class="lectura">
<p class="entradilla">David Jiménez escribió su libro con dos reglas: los políticos, empresarios y miembros de la monarquía aparecen con nombre y apellidos; los periodistas y directivos del diario, con apodos. La película cambia algunos nombres más.</p>
<p>Cada fila lleva un sello: <span class="sello s-conf">Confirmado</span> cuando lo publican el autor, la productora o varios medios; <span class="sello s-real">Nombre real</span> cuando la persona aparece con su nombre en el libro; <span class="sello s-pend">Pendiente</span> cuando aún no hay datos fiables.</p>
</div>

<h2>Confirmados</h2>
<div class="tabla"><table>
<caption>Persona real, libro y película</caption>
<thead><tr><th>Persona real</th><th>En el libro</th><th>En la película</th><th>Actor</th><th>Certeza</th></tr></thead>
<tbody>
<tr><td><a href="{{r}}personajes/david-jimenez/">David Jiménez</a>, director de <i>El Mundo</i> (2015-2016)</td><td>Él mismo, narrador</td><td>David Jiménez</td><td>David Verdaguer</td><td><span class="sello s-conf">Confirmado</span></td></tr>
<tr><td><a href="{{r}}personajes/cardenal/">Antonio Fernández-Galiano</a>, presidente de Unidad Editorial</td><td>“El Cardenal”</td><td>Cardenal, el editor</td><td>Alberto San Juan</td><td><span class="sello s-conf">Confirmado</span></td></tr>
</tbody></table></div>

<h2>Con su nombre real en el libro</h2>
<div class="tabla"><table>
<caption>Figuras públicas citadas por su nombre</caption>
<thead><tr><th>Persona</th><th>Papel en el libro</th><th>En la película</th><th>Certeza</th></tr></thead>
<tbody>
<tr><td>Pedro J. Ramírez</td><td>Fundador y director histórico de <i>El Mundo</i>; su salida precede a los hechos</td><td>Por confirmar</td><td><span class="sello s-real">Nombre real</span></td></tr>
<tr><td>Casimiro García-Abadillo</td><td>Director anterior, al que Jiménez sustituye</td><td>Por confirmar</td><td><span class="sello s-real">Nombre real</span></td></tr>
<tr><td>César Alierta</td><td>Empresario; según el autor, parte del sistema de “Los Acuerdos”</td><td>Por confirmar</td><td><span class="sello s-real">Nombre real</span></td></tr>
<tr><td>Florentino Pérez</td><td>Empresario; según el autor, parte del sistema de “Los Acuerdos”</td><td>Por confirmar</td><td><span class="sello s-real">Nombre real</span></td></tr>
</tbody></table></div>

<h2 id="pendientes">Apodos del libro pendientes de confirmar</h2>
<div class="lectura">
<p>El libro usa apodos para la gente de la redacción y la dirección del diario: “La Digna”, “El Señorito”, “Rasputín”, “El Poeta”, “El Secretario”, “El Reportero”, “los inspirados” o “los de la segunda planta”, entre otros. Algunos medios han publicado a quién corresponden, pero todavía no tenemos fuentes suficientes para afirmarlo, ni sabemos qué personaje de la película los representa. Actualizaremos esta tabla tras el estreno.</p>
</div>
<div class="tabla"><table>
<caption>Reparto sin personaje publicado</caption>
<thead><tr><th>Actor o actriz</th><th>Personaje</th><th>Certeza</th></tr></thead>
<tbody>
<tr><td>Fernando Colomo</td><td>Por confirmar (la crítica lo describe como un mentor)</td><td><span class="sello s-pend">Pendiente</span></td></tr>
<tr><td>Carmen Machi · Emma Vilarasau · Guillermo Toledo · Fernando Cayo</td><td>Por confirmar (colaboraciones especiales)</td><td><span class="sello s-pend">Pendiente</span></td></tr>
<tr><td>Xavi Sáez · Miriam Iscla · Joan Carreras · Anna Alarcón · Nacho Fresneda · Pau Durà · Marc Rodríguez · David Vert · Mia Sala-Patau</td><td>Por confirmar</td><td><span class="sello s-pend">Pendiente</span></td></tr>
</tbody></table></div>
{fuentes("wiki_libro", "wiki_peli", "infobae", "cineconn", "cinemagavia", "ecartelera", "av451")}
{siguiente(("Ficha", "El Cardenal", "personajes/cardenal/"), ("Ficha", "David Jiménez", "personajes/david-jimenez/"), ("Contexto", "La historia real", "historia-real/"))}
</div>""",
    ld=[ld_migas([("Inicio", ""), ("Quién es quién", "personajes/")]),
        {"@type": "ItemList", "name": "Personajes confirmados de El Director", "itemListElement": [
            {"@type": "ListItem", "position": 1, "url": SITE + "personajes/david-jimenez/", "name": "David Jiménez"},
            {"@type": "ListItem", "position": 2, "url": SITE + "personajes/cardenal/", "name": "Cardenal"}]}],
)

# ---------------- CARDENAL ----------------
PAGINAS["personajes/cardenal/"] = dict(
    titulo="Quién es el Cardenal en El Director: Antonio Fernández-Galiano",
    desc="El Cardenal de El Director es Antonio Fernández-Galiano, presidente de Unidad Editorial. En la película lo interpreta Alberto San Juan.",
    activo="personajes/",
    cuerpo=f"""<div class="contenedor">
{migas(("Inicio", ""), ("Quién es quién", "personajes/"), ("El Cardenal", None))}
<p class="antetitulo">Ficha de personaje</p>
<h1>¿Quién es el Cardenal en <span class="el">El</span> Director?</h1>
<div class="lectura">
<p class="entradilla"><strong>El Cardenal es Antonio Fernández-Galiano</strong>, presidente de Unidad Editorial, la empresa que publica <i>El Mundo</i>, cuando David Jiménez dirigió el periódico. En la película se llama Cardenal y lo interpreta <strong>Alberto San Juan</strong>.</p>
<p><span class="sello s-conf">Confirmado</span></p>
</div>
<div class="ficha-cabecera">
  <div><div class="antetitulo">Vida real</div><div class="par" style="border:0;padding:0;display:block"><div class="nombre">Antonio Fernández-Galiano</div><div class="detalle">Presidente de Unidad Editorial</div></div></div>
  <div class="igual" style="font-family:var(--f-display);font-size:2rem;color:var(--oro)" aria-hidden="true">=</div>
  <div class="der"><div class="antetitulo">Película</div><div class="par" style="border:0;padding:0;display:block"><div class="nombre">Cardenal</div><div class="detalle">Alberto San Juan</div></div></div>
</div>
<dl class="datos">
  <dt>En el libro</dt><dd>“El Cardenal”, apodo</dd>
  <dt>En la película</dt><dd>Cardenal, el editor del diario</dd>
  <dt>Actor</dt><dd>Alberto San Juan</dd>
  <dt>Fuentes</dt><dd>Wikipedia (libro), Infobae y Cineconn (película)</dd>
</dl>
<div class="lectura">
<h2>En el libro</h2>
<p>Fernández-Galiano es quien ofrece a Jiménez la dirección de <i>El Mundo</i> en 2015. Jiménez lo identifica con el apodo de “El Cardenal”, uno de los que usa para la dirección y la redacción del diario. Tras su despido en 2016, Jiménez demandó a la empresa; según Wikipedia, ambas partes llegaron a un acuerdo económico que no impedía publicar el libro.</p>
<h2>En la película</h2>
<p>La sinopsis oficial lo presenta como el editor que protege los intereses ocultos del diario, con los que choca la idea de periodismo riguroso del nuevo director. Infobae indicó en julio de 2026 que el personaje está inspirado en Fernández-Galiano.</p>
</div>
<div class="recorte">
  <p><strong>Sinopsis oficial</strong></p>
  <p>Un corresponsal con más de veinte años cubriendo guerras es nombrado director de un gran diario nacional. Su defensa del periodismo riguroso choca con los intereses ocultos del periódico, protegidos por Cardenal, el editor.</p>
  <p style="font-size:.8rem">Resumen de la sinopsis de <a href="{BETA}" rel="noopener">Beta Fiction Spain</a></p>
</div>
<h2 id="donde">Léelo y míralo</h2>
<p class="lectura">El libro cuenta la versión de Jiménez con más detalle que la película. La película llega a los cines el 20 de noviembre.</p>
<div class="acciones"><a class="btn" href="{{r}}libro/#donde-leer">Dónde leer el libro</a><a class="btn sec" href="{{r}}pelicula/#donde-ver">Dónde ver la película</a></div>
{fuentes("wiki_libro", "infobae", "cineconn", "beta")}
{siguiente(("Ficha", "David Jiménez", "personajes/david-jimenez/"), ("Tabla", "Todos los personajes", "personajes/"), ("Contexto", "La historia real", "historia-real/"))}
</div>""",
    ld=[ld_migas([("Inicio", ""), ("Quién es quién", "personajes/"), ("El Cardenal", "personajes/cardenal/")]),
        {"@type": "Person", "name": "Antonio Fernández-Galiano", "jobTitle": "Presidente de Unidad Editorial",
         "sameAs": []},
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": "¿Quién es el Cardenal en El Director?",
          "acceptedAnswer": {"@type": "Answer", "text": "El Cardenal es Antonio Fernández-Galiano, presidente de Unidad Editorial cuando David Jiménez dirigió El Mundo. En la película lo interpreta Alberto San Juan."}}]}],
)

# ---------------- DAVID JIMÉNEZ ----------------
PAGINAS["personajes/david-jimenez/"] = dict(
    titulo="David Jiménez, autor y protagonista de El Director",
    desc="David Jiménez, corresponsal de guerra y director de El Mundo entre 2015 y 2016, escribió El Director. En la película lo interpreta David Verdaguer.",
    activo="personajes/",
    cuerpo=f"""<div class="contenedor">
{migas(("Inicio", ""), ("Quién es quién", "personajes/"), ("David Jiménez", None))}
<p class="antetitulo">Ficha de personaje · Autor</p>
<h1>David Jiménez</h1>
<div class="lectura">
<p class="entradilla">Periodista y escritor, nacido en Barcelona en 1971. Fue corresponsal de <i>El Mundo</i> en Asia durante casi dos décadas y dirigió el periódico entre abril de 2015 y mayo de 2016. Es el autor del libro y el protagonista de la película, donde lo interpreta <strong>David Verdaguer</strong>.</p>
<p><span class="sello s-conf">Confirmado</span></p>
</div>
<dl class="datos">
  <dt>En el libro</dt><dd>Narrador en primera persona</dd>
  <dt>En la película</dt><dd>David Jiménez</dd>
  <dt>Actor</dt><dd>David Verdaguer</dd>
  <dt>Director de El Mundo</dt><dd>30 de abril de 2015 – 25 de mayo de 2016</dd>
</dl>
<div class="lectura">
<h2>Trayectoria</h2>
<p>Entró en <i>El Mundo</i> en los años noventa y en 1998 abrió la primera delegación del periódico en Asia, en Hong Kong. Cubrió conflictos en Timor Oriental, Cachemira, Afganistán, Birmania y Nepal, entró dos veces en Corea del Norte y se quedó en Fukushima tras el accidente nuclear. Fue Nieman Fellow en la Universidad de Harvard y columnista de <i>The New York Times</i>.</p>
<p>Sustituyó a Casimiro García-Abadillo al frente del periódico y fue despedido algo más de un año después; le sucedió Pedro García Cuartango. Demandó a la empresa y el despido se reconoció como improcedente.</p>
<h2>Libros</h2>
<ul>
<li><i>Hijos del monzón</i> (2007)</li>
<li><i>El botones de Kabul</i> (novela)</li>
<li><i>El lugar más feliz del mundo</i> (2013)</li>
<li><i>El director</i> (2019)</li>
<li><i>El corresponsal</i> (2022, novela)</li>
<li><i>Los diarios del opio</i> (2023)</li>
<li><i>Días salvajes</i> (2024)</li>
</ul>
<h2>Hoy</h2>
<p>Mantiene un <a href="{YOUTUBE}" rel="noopener">canal de YouTube</a> con su nombre, dedicado a la actualidad política y mediática.</p>
</div>
<div class="acciones"><a class="btn" href="{{r}}libro/#donde-leer">Dónde leer el libro</a><a class="btn sec" href="{{r}}pelicula/#donde-ver">Dónde ver la película</a></div>
{fuentes("wiki_autor", "wiki_libro", "wiki_peli", "youtube")}
{siguiente(("Ficha", "El Cardenal", "personajes/cardenal/"), ("Libro", "El director (2019)", "libro/"), ("Contexto", "La historia real", "historia-real/"))}
</div>""",
    ld=[ld_migas([("Inicio", ""), ("Quién es quién", "personajes/"), ("David Jiménez", "personajes/david-jimenez/")]),
        {"@type": "Person", "@id": SITE + "personajes/david-jimenez/#persona", "name": "David Jiménez García",
         "birthDate": "1971-01-11", "birthPlace": "Barcelona", "jobTitle": "Periodista y escritor",
         "sameAs": [F["wiki_autor"][1], YOUTUBE]}],
)

# ---------------- LIBRO ----------------
PAGINAS["libro/"] = dict(
    titulo="El director, el libro de David Jiménez: sinopsis y dónde leerlo",
    desc="El director (Libros del K.O., 2019): el año de David Jiménez al frente de El Mundo y “Los Acuerdos” entre prensa y poder. Sinopsis, datos y dónde leerlo.",
    activo="libro/",
    cuerpo=f"""<div class="contenedor">
{migas(("Inicio", ""), ("El libro", None))}
<p class="antetitulo">El libro</p>
<h1><span class="el">El</span> director <span style="font-size:.45em;display:block;letter-spacing:.06em;color:var(--gris);margin-top:8px">Secretos e intrigas de la prensa narrados por el exdirector de El Mundo</span></h1>
<dl class="datos">
  <dt>Autor</dt><dd><a href="{{r}}personajes/david-jimenez/">David Jiménez García</a></dd>
  <dt>Editorial</dt><dd>Libros del K.O.</dd>
  <dt>Publicación</dt><dd>8 de abril de 2019 · edición en catalán el mismo año</dd>
  <dt>Páginas</dt><dd>328</dd>
  <dt>ISBN</dt><dd class="mono">978-84-17678-08-1</dd>
  <dt>Género</dt><dd>No ficción (crónica, memorias)</dd>
</dl>
<div class="lectura">
<h2>De qué trata</h2>
<p>En 2015, después de veinte años como corresponsal en Asia, Jiménez acepta dirigir <i>El Mundo</i>. Llega con la idea de hacer un periódico independiente y se encuentra con un sistema de pactos y favores entre el poder político, el económico y la prensa, al que llama “Los Acuerdos”. Se niega a participar, recibe presiones desde fuera y desde la propia redacción, y es despedido al cabo de un año.</p>
<p>El libro se convirtió en un éxito de ventas. Algunos periodistas mencionados negaron parte de lo que cuenta.</p>
<h2>Nombres y apodos</h2>
<p>Los políticos, empresarios, periodistas de otros medios y miembros de la monarquía aparecen con nombre y apellidos. A la gente de la redacción y de la dirección del periódico, Jiménez les pone apodos: “El Cardenal”, “La Digna”, “El Señorito”, “Rasputín”… <a href="{{r}}personajes/">Mira quién es quién</a>.</p>
<h2>La portada</h2>
<p>La diseñó el estudio Cover Kitchen con ejemplares antiguos de <i>El Mundo</i> que aportó el autor: trituraron páginas de economía y política, hicieron un collage y lo convirtieron en una máscara, un retrato de la cara oculta de los medios.</p>
<h2 id="donde-leer">Dónde leer el libro</h2>
<p>Enlaces informativos, sin afiliación.</p>
</div>
{DONDE_LEER}
{fuentes("wiki_libro", "coverkitchen", "elsalto")}
{siguiente(("Película", "El director (2026)", "pelicula/"), ("Tabla", "Quién es quién", "personajes/"), ("Autor", "David Jiménez", "personajes/david-jimenez/"))}
</div>""",
    ld=[ld_migas([("Inicio", ""), ("El libro", "libro/")]), LIBRO_LD],
)

# ---------------- PELÍCULA ----------------
PAGINAS["pelicula/"] = dict(
    titulo="El director (2026), la película: reparto, estreno y personajes",
    desc="El director, película de Dani de la Orden con David Verdaguer y Alberto San Juan, basada en el libro de David Jiménez. Estreno en cines el 20 de noviembre de 2026.",
    activo="pelicula/",
    cuerpo=f"""<div class="contenedor">
{migas(("Inicio", ""), ("La película", None))}
<p class="antetitulo">La película · Estreno el 20 de noviembre de 2026</p>
<h1><span class="el">El</span> director <span style="font-size:.45em;display:block;letter-spacing:.14em;color:var(--oro);margin-top:8px">La verdad tiene un precio</span></h1>
<div class="lectura">
<p class="entradilla">Un corresponsal con más de veinte años cubriendo guerras es nombrado director de uno de los principales diarios del país. Su defensa del periodismo riguroso choca desde el principio con los intereses ocultos del periódico, protegidos por Cardenal, el editor.</p>
</div>
<dl class="datos">
  <dt>Dirección</dt><dd>Dani de la Orden</dd>
  <dt>Guion</dt><dd>Alejandro Hernández y Michel Gaztambide, sobre el libro de David Jiménez</dd>
  <dt>Fotografía</dt><dd>Maria Codina</dd>
  <dt>Música</dt><dd>Maria Chiara Casà</dd>
  <dt>Producción</dt><dd>Beta Fiction Spain, Sábado Time, Cardinal Content e Historias de un Director SL, con la participación de HBO Max, RTVE y 3Cat</dd>
  <dt>Distribución</dt><dd>Beta Fiction Spain</dd>
  <dt>Género</dt><dd>Thriller, drama</dd>
  <dt>Estreno</dt><dd>20 de noviembre de 2026, en cines. Algunos medios publicaron el 27; el cartel oficial dice 20.</dd>
</dl>
<h2>Reparto</h2>
<div class="tabla"><table>
<thead><tr><th>Actor o actriz</th><th>Personaje</th><th>Inspirado en</th></tr></thead>
<tbody>
<tr><td>David Verdaguer</td><td>David Jiménez</td><td><a href="{{r}}personajes/david-jimenez/">David Jiménez</a></td></tr>
<tr><td>Alberto San Juan</td><td>Cardenal</td><td><a href="{{r}}personajes/cardenal/">Antonio Fernández-Galiano</a></td></tr>
<tr><td>Fernando Colomo</td><td>Por confirmar</td><td>—</td></tr>
<tr><td>Xavi Sáez · Miriam Iscla · Joan Carreras</td><td>Por confirmar</td><td>—</td></tr>
<tr><td>Carmen Machi · Emma Vilarasau · Guillermo Toledo · Fernando Cayo</td><td>Colaboración especial · por confirmar</td><td>—</td></tr>
<tr><td>Anna Alarcón · Nacho Fresneda · Pau Durà · Marc Rodríguez · David Vert · Mia Sala-Patau</td><td>Por confirmar</td><td>—</td></tr>
</tbody></table></div>
<div class="lectura">
<h2>Cómo se ve</h2>
<p>La crítica destaca una fotografía de luz fría y planos muy abiertos que aíslan al protagonista en salas de reuniones, el uso de imágenes de archivo de informativos y un ritmo de thriller. El proyecto nació como serie antes de convertirse en película.</p>
<h2 id="donde-ver">Dónde ver la película</h2>
<p>En cines desde el 20 de noviembre. Enlaces informativos, sin afiliación.</p>
</div>
{DONDE_VER}
{fuentes("beta", "av451", "wiki_peli", "infobae", "cineconn", "cinemagavia", "ecartelera")}
{siguiente(("Tabla", "Quién es quién", "personajes/"), ("Libro", "El director (2019)", "libro/"), ("Contexto", "La historia real", "historia-real/"))}
</div>""",
    ld=[ld_migas([("Inicio", ""), ("La película", "pelicula/")]), PELI_LD],
)

# ---------------- HISTORIA REAL ----------------
PAGINAS["historia-real/"] = dict(
    titulo="¿Es real El Director? La historia de David Jiménez en El Mundo",
    desc="El Director está basada en hechos reales: el año de David Jiménez como director de El Mundo (2015-2016). Cronología, “Los Acuerdos” y del libro a la película.",
    activo="historia-real/",
    cuerpo=f"""<div class="contenedor">
{migas(("Inicio", ""), ("Historia real", None))}
<p class="antetitulo">Historia real</p>
<h1>¿Es real <span class="el">El</span> Director?</h1>
<div class="lectura">
<p class="entradilla">Sí. La película se basa en el libro en el que David Jiménez cuenta su año como director de <i>El Mundo</i>, entre abril de 2015 y mayo de 2016. Es una adaptación de ficción: cambia nombres y condensa hechos.</p>
<h2>“Los Acuerdos”</h2>
<p>Es el nombre que Jiménez da al sistema de pactos y favores entre los grandes poderes económicos y políticos y la prensa. En el libro sitúa en ese sistema a máximos dirigentes empresariales como César Alierta o Florentino Pérez. Su negativa a participar es, según su relato, el origen de las presiones y de su despido.</p>
</div>
<h2>Cronología</h2>
<ol class="cronologia">
<li><time>1998</time>Jiménez abre en Hong Kong la primera delegación de <i>El Mundo</i> en Asia.</li>
<li><time>2014</time>Pedro J. Ramírez, fundador del periódico, deja la dirección. Le sustituye Casimiro García-Abadillo.</li>
<li><time>30 de abril de 2015</time>David Jiménez es nombrado director de <i>El Mundo</i>, a propuesta del presidente de Unidad Editorial, Antonio Fernández-Galiano.</li>
<li><time>25 de mayo de 2016</time>Jiménez deja la dirección tras su despido. Le sucede Pedro García Cuartango. Demanda a la empresa y el despido se reconoce como improcedente.</li>
<li><time>8 de abril de 2019</time>Libros del K.O. publica <i>El director</i>.</li>
<li><time>Octubre de 2025</time>Beta Fiction adquiere los derechos de adaptación.</li>
<li><time>Febrero de 2026</time>Rodaje dirigido por Dani de la Orden.</li>
<li><time>Julio de 2026</time>Primeras imágenes y tráiler.</li>
<li><time>20 de noviembre de 2026</time>Estreno en cines.</li>
</ol>
<div class="lectura">
<h2>Qué cambia del libro a la película</h2>
<p>La película mantiene el nombre del protagonista y convierte en personajes de ficción a otras figuras del libro, como el editor Cardenal. Publicaremos una comparación detallada después del estreno.</p>
</div>
<div class="acciones"><a class="btn" href="{{r}}personajes/">Ver quién es quién</a><a class="btn sec" href="{{r}}libro/#donde-leer">Dónde leer el libro</a></div>
{fuentes("wiki_libro", "wiki_autor", "wiki_peli", "elsalto", "infobae")}
{siguiente(("Tabla", "Quién es quién", "personajes/"), ("Libro", "El director (2019)", "libro/"), ("Película", "El director (2026)", "pelicula/"))}
</div>""",
    ld=[ld_migas([("Inicio", ""), ("Historia real", "historia-real/")])],
)

# ---------------- FAQ ----------------
FAQ = [
    ("¿El Director está basada en hechos reales?", "Sí. Adapta el libro de David Jiménez sobre su año como director de El Mundo (2015-2016). La película es una ficción inspirada en esos hechos y cambia algunos nombres."),
    ("¿Quién es el Cardenal en El Director?", "Es Antonio Fernández-Galiano, presidente de Unidad Editorial cuando Jiménez dirigió El Mundo. En la película lo interpreta Alberto San Juan."),
    ("¿Quién interpreta a David Jiménez?", "David Verdaguer."),
    ("¿Cuándo se estrena El Director?", "El 20 de noviembre de 2026 en cines de España, según el cartel oficial y la distribuidora. Algunos medios publicaron el 27 de noviembre."),
    ("¿Quién dirige la película?", "Dani de la Orden, con guion de Alejandro Hernández y Michel Gaztambide."),
    ("¿Qué periódico es el de El Director?", "El libro trata de El Mundo, el diario que Jiménez dirigió. En la película se presenta como un importante diario nacional."),
    ("¿Qué son “Los Acuerdos”?", "Es el nombre que Jiménez da al sistema de pactos y favores entre el poder económico, el político y la prensa que describe en el libro."),
    ("¿Quiénes son La Digna, El Señorito o Rasputín?", "Son apodos que Jiménez usa en el libro para periodistas y directivos del periódico. Aún no tenemos fuentes suficientes para confirmar a quién corresponden ni su personaje en la película."),
    ("¿Es esta la web oficial?", "No. Es un proyecto informativo e independiente, sin publicidad ni enlaces de afiliado."),
]
PAGINAS["preguntas-frecuentes/"] = dict(
    titulo="Preguntas frecuentes sobre El Director, libro y película",
    desc="¿Es real El Director? ¿Quién es el Cardenal? ¿Cuándo se estrena? Respuestas cortas sobre el libro de David Jiménez y la película de Dani de la Orden.",
    activo="preguntas-frecuentes/",
    cuerpo=f"""<div class="contenedor">
{migas(("Inicio", ""), ("Preguntas frecuentes", None))}
<p class="antetitulo">Preguntas frecuentes</p>
<h1>Preguntas sobre <span class="el">El</span> Director</h1>
<dl class="faq lectura">{"".join(f"<dt>{q}</dt><dd>{a}</dd>" for q, a in FAQ)}</dl>
{fuentes("wiki_libro", "wiki_peli", "beta", "av451", "infobae")}
</div>""",
    ld=[ld_migas([("Inicio", ""), ("Preguntas frecuentes", "preguntas-frecuentes/")]),
        {"@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ]}],
)

# ---------------- METODOLOGÍA ----------------
PAGINAS["metodologia-y-fuentes/"] = dict(
    titulo="Metodología, fuentes y aviso legal · El Director",
    desc="Cómo verificamos la relación entre personas reales y personajes de El Director, qué fuentes usamos y cómo pedir una rectificación.",
    cuerpo=f"""<div class="contenedor">
{migas(("Inicio", ""), ("Metodología y fuentes", None))}
<p class="antetitulo">Transparencia</p>
<h1>Metodología, fuentes y aviso legal</h1>
<div class="lectura">
<h2>Qué es esta web</h2>
<p>“El Director. Del libro a la película” es un proyecto independiente con fines informativos. No es la web oficial del libro, de la película ni de su autor, y no está vinculado a Libros del K.O., Beta Fiction Spain ni David Jiménez. No tiene publicidad, enlaces de afiliado ni cookies, y no recibe dinero de nadie. Los enlaces a librerías y cines son solo informativos.</p>
<h2>Cómo verificamos</h2>
<ul>
<li><span class="sello s-conf">Confirmado</span> Lo publican el autor, la productora o la distribuidora, o al menos dos medios independientes.</li>
<li><span class="sello s-real">Nombre real</span> La persona aparece con su nombre en el libro, según fuentes publicadas.</li>
<li><span class="sello s-pend">Pendiente</span> No hay fuentes suficientes. No asociamos a ninguna persona real con un apodo o un personaje hasta tenerlas.</li>
</ul>
<p>Recogemos lo que ya han publicado el autor y otros medios, enlazamos las fuentes en cada página e indicamos la fecha de actualización. No emitimos juicios sobre las personas mencionadas. La película es una obra de ficción inspirada en hechos reales.</p>
<p>No usamos fotografías de personas reales ni material gráfico de la película sin autorización. Las marcas y títulos citados pertenecen a sus titulares.</p>
<h2 id="rectificaciones">Rectificaciones</h2>
<p>Si eres una de las personas mencionadas o ves un error, <a href="{ISSUES}" rel="noopener">abre una incidencia en el repositorio de la web</a> (necesitas una cuenta de GitHub). Revisaremos cada petición en un máximo de 72 horas y corregiremos lo que proceda, indicando la fecha del cambio.</p>
<h2>Fuentes consultadas</h2>
<ul>{"".join(f'<li><a href="{u}" rel="noopener">{t}</a></li>' for t, u in F.values())}</ul>
<p class="actualizado">Actualizado el {ACTUALIZADO_TXT}</p>
</div>
</div>""",
    ld=[ld_migas([("Inicio", ""), ("Metodología y fuentes", "metodologia-y-fuentes/")])],
)

NO_ENCONTRADA = """<div class="contenedor"><p class="antetitulo">Error 404</p><h1>Esta página no está en la edición de hoy</h1>
<p class="lectura">Puede que la dirección esté mal escrita o que hayamos movido el contenido.</p>
<div class="acciones"><a class="btn" href="/{repo}/">Ir a la portada</a><a class="btn sec" href="/{repo}/personajes/">Ver quién es quién</a></div></div>"""

ICONO = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" fill="#0f2a2c"/><text x="32" y="46" font-family="Georgia,serif" font-size="40" font-weight="700" text-anchor="middle" fill="#e3b23c">D</text></svg>"""

def main():
    docs = SALIDA
    if os.path.isdir(docs):
        shutil.rmtree(docs)
    os.makedirs(os.path.join(docs, "assets"))
    base = os.path.dirname(os.path.abspath(__file__))
    shutil.copy(os.path.join(base, "assets", "estilos.css"), os.path.join(docs, "assets", "estilos.css"))
    open(os.path.join(docs, "assets", "icono.svg"), "w").write(ICONO)
    open(os.path.join(docs, ".nojekyll"), "w").write("")
    for ruta, p in PAGINAS.items():
        destino = os.path.join(docs, ruta, "index.html")
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        with open(destino, "w", encoding="utf-8") as fh:
            fh.write(plantilla(ruta, p["titulo"], p["desc"], p["cuerpo"], p.get("ld"), p.get("activo"), p.get("portada", False)))
    # 404 con rutas absolutas (GitHub Pages la sirve en cualquier profundidad)
    pagina404 = plantilla("", "Página no encontrada · El Director", "Página no encontrada.", NO_ENCONTRADA.format(repo=REPO))
    pagina404 = pagina404.replace('href="assets/', f'href="/{REPO}/assets/').replace('<meta name="robots" content="index, follow, max-image-preview:large">', '<meta name="robots" content="noindex">')
    for u, _ in MENU + [("metodologia-y-fuentes/", ""), ("personajes/", ""), ("libro/", ""), ("pelicula/", ""), ("historia-real/", ""), ("personajes/david-jimenez/", ""), ("preguntas-frecuentes/", ""), ("metodologia-y-fuentes/#rectificaciones", "")]:
        pagina404 = pagina404.replace(f'href="{u}"', f'href="/{REPO}/{u}"')
    pagina404 = pagina404.replace('<a class="marca" href="">', f'<a class="marca" href="/{REPO}/">')
    open(os.path.join(docs, "404.html"), "w", encoding="utf-8").write(pagina404)
    urls = "".join(f"<url><loc>{SITE}{r}</loc><lastmod>{ACTUALIZADO}</lastmod></url>" for r in PAGINAS)
    open(os.path.join(docs, "sitemap.xml"), "w").write(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>')
    # robots.txt solo es efectivo en la raíz del dominio; se deja por si se usa dominio propio
    open(os.path.join(docs, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {SITE}sitemap.xml\n")
    print(f"{len(PAGINAS)} páginas generadas en {docs} para {SITE}")

if __name__ == "__main__":
    main()
