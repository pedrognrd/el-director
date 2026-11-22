#!/usr/bin/env python3
"""Genera el sitio estático "El Director. Del libro a la película".

Uso:  python3 build.py [usuario-github] [repositorio]
Escribe los HTML en ./docs (carpeta que publica GitHub Pages).
"""
import json, os, sys, shutil, html

USUARIO = sys.argv[1] if len(sys.argv) > 1 else "pedrognrd"
REPO = sys.argv[2] if len(sys.argv) > 2 else "el-director"
# Dominio propio (GitHub Pages lo sirve gracias al archivo CNAME de docs/)
DOMINIO = "eldirectorquienesquien.com"
# Google Analytics 4 (solo se carga si la persona acepta en el aviso de cookies). Vacío = sin Analytics ni aviso.
GA_ID = "G-KYJ48RR145"
SITE = f"https://{DOMINIO}/"
RAIZ = "/"   # ruta absoluta de la web en el dominio (antes /el-director/)
ISSUES = f"https://github.com/{USUARIO}/{REPO}/issues/new"
ACTUALIZADO = "2026-11-17"
ACTUALIZADO_TXT = "17 de noviembre de 2026"
import hashlib
_BASE = os.path.dirname(os.path.abspath(__file__))
# Versión de los recursos para evitar que el navegador use CSS/JS antiguos en caché
VERSION = hashlib.md5(b"".join(open(os.path.join(_BASE, "assets", f), "rb").read() for f in ("estilos.css", "video.js", "slider.js", "encuesta.js", "cookies.js"))).hexdigest()[:8]
# Supabase (encuesta). La clave es la pública (publishable / anon): va en la web por diseño.
# Si la clave está vacía, la encuesta funciona en modo prueba (votos solo en el navegador).
SUPABASE_URL = "https://chfqajnvbydhopqglsfj.supabase.co"
SUPABASE_KEY = "sb_publishable__lsAxOw4mUCSPmH-8cjugg_9JSWLt6K"
CREDITOS_LIBRO = json.load(open(os.path.join(_BASE, "datos", "creditos-libro.json"), encoding="utf-8"))
SALIDA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")

MENU = [
    ("personajes/", "Quién es quién"),
    ("libro/", "El libro"),
    ("pelicula/", "La película"),
    ("historia-real/", "Historia real"),
    ("preguntas-frecuentes/", "Preguntas"),
    ("encuesta/", "Encuesta"),
]

# ---------- Enlaces externos ----------
AMAZON = "https://amzn.eu/d/0aOE6Rxm"
TODOSTUSLIBROS = "https://www.todostuslibros.com/busquedas?keyword=9788417678081"
MARCIALPONS = "https://www.marcialpons.es/libros/el-director/9788417678081/"
LIBROSDELKO = "https://www.librosdelko.com/"
BETA = "https://betafiction.es/cine/el-director/"
TAQUILLA = "https://www.taquilla.com/entradas/el-director-2026"
YOUTUBE = "https://www.youtube.com/@DavidJimenezElDirector"

# ---------- Imágenes con licencia libre (Wikimedia Commons) ----------
FOTOS = {
    "david-jimenez": ("David Jiménez en 2019", "Cristina Pozo García (eldiario.es)", "CC BY-SA 3.0 ES",
                      "https://creativecommons.org/licenses/by-sa/3.0/es/",
                      "https://commons.wikimedia.org/wiki/File:El_exdirector_de_El_Mundo_David_Jim%C3%A9nez.jpg"),
    "dani-de-la-orden": ("Dani de la Orden en 2013", "Barcelona.cat", "CC BY 3.0",
                         "https://creativecommons.org/licenses/by/3.0/",
                         "https://commons.wikimedia.org/wiki/File:(Dani_de_la_Orden)_La_hist%C3%B2ria_rom%C3%A0ntica_de_Barcelona.jpg"),
}

# Fotos ilustrativas de la cabecera y figuras recortadas
CABECERA = [
    ("cabecera-rotativa.jpg", "Rotativa del diario Euzkadi", "Theklan", "CC BY-SA 4.0", "https://creativecommons.org/licenses/by-sa/4.0/",
     "https://commons.wikimedia.org/wiki/File:Euzkadi_egunkariaren_errotatiba_02.jpg"),
    ("cabecera-redaccion.jpg", "Redacción de un diario", "JD Lasica", "CC BY 2.0", "https://creativecommons.org/licenses/by/2.0/",
     "https://commons.wikimedia.org/wiki/File:El_Mercurio_newsroom_(6098651486).jpg"),
    ("cabecera-rueda-prensa.jpg", "Fotógrafos en una rueda de prensa", "Arne Schambeck / Bundesarchiv", "CC BY-SA 3.0 DE",
     "https://creativecommons.org/licenses/by-sa/3.0/de/",
     "https://commons.wikimedia.org/wiki/File:Bundesarchiv_B_145_Bild-F083629-0025,_Bonn,_Fotoreporter_auf_Pressekonferenz_P%C3%B6hl.jpg"),
]
SILUETAS = [
    ("silueta-hombre.png", "Silueta de hombre", "Burst (StockSnap)", "CC0", "https://creativecommons.org/publicdomain/zero/1.0/",
     "https://stocksnap.io/photo/businessman-thinking-TGG4JHNHB8"),
    ("silueta-mujer.png", "Silueta de mujer", "StockSnap", "CC0", "https://creativecommons.org/publicdomain/zero/1.0/",
     "https://stocksnap.io/photo/business-woman-FPQIEQBMPA"),
]

def credito_corto(clave):
    _, autor, lic, lic_url, origen = FOTOS[clave]
    return f'{autor}, {lic}'  # sin enlaces: va dentro de una tarjeta enlazada; los enlaces están en Créditos

TAM_FIGURAS = {"silueta-hombre.png": (337, 640), "silueta-mujer.png": (403, 640), "figura-personaje-cardenal.png": (503, 640),
               "figura-david-jimenez.png": (640, 611), "figura-personaje-david.png": (556, 640)}

def luchador(img, alt, real=False, duda=False, lado="izq"):
    clases = "luchador " + lado + (" real" if real else "") + (" duda" if duda else "")
    w, h = TAM_FIGURAS[img]
    return f'<figure class="{clases}"><img src="{{r}}assets/img/{img}" alt="{alt}" width="{w}" height="{h}" decoding="async"></figure>'

def combate(enlace, izq, der, nombres, credito, signo="="):
    (n1, d1), (n2, d2) = nombres
    return f"""<a class="combate" href="{{r}}{enlace}">
  <div class="esquinas"><span>Vida real</span><span>Película</span></div>
  <div class="ring">{izq}<span class="contra" aria-hidden="true">{signo}</span>{der}</div>
  <div class="nombres">
    <div><strong>{n1}</strong><span>{d1}</span></div>
    <div class="der"><strong>{n2}</strong><span>{d2}</span></div>
  </div>
</a>"""

DONDE_FOTO = {
    "david-jimenez": "Portada (slider), ficha de David Jiménez (también como cabecera, volteada en horizontal)",
    "dani-de-la-orden": "Película",
}
DONDE_VIDEO = {
    "PUQzmris2CE": "Portada, película",
    "NT7O8rzR3PU": "Película",
    "ORXNiBTK5rc": "Ficha de David Jiménez",
    "CgmhIDMm-B4": "Película",
}

def foto(clave, rotulo, ficcion=False, carga="lazy"):
    alt, autor, lic, lic_url, origen = FOTOS[clave]
    clase = "foto ficcion" if ficcion else "foto"
    return (f'<figure class="{clase}"><div class="marco"><img src="{{r}}assets/img/{clave}.jpg" alt="{alt}" width="480" height="600" loading="{carga}" decoding="async"></div>'
            f'<figcaption><strong>{rotulo}</strong></figcaption></figure>')

def foto_kit(ruta, alt, rotulo):
    return (f'<figure class="foto ficcion"><div class="marco"><img src="{{r}}assets/img/{ruta}" alt="{alt}" width="480" height="600" decoding="async"></div>'
            f'<figcaption><strong>{rotulo}</strong></figcaption></figure>')

def silueta(rotulo):
    return (f'<figure class="foto"><div class="marco"><img src="{{r}}assets/img/silueta.svg" alt="Silueta: no hay foto con licencia libre" width="480" height="600" loading="lazy"></div>'
            f'<figcaption><strong>{rotulo}</strong></figcaption></figure>')

# ---------- Vídeos (YouTube, modo de privacidad mejorada) ----------
VIDEOS = {
    "PUQzmris2CE": ("El Director · Teaser tráiler", "Beta Fiction Spain", "PT1M7S", "2026-07-09", "1:07"),
    "NT7O8rzR3PU": ("El Director, 20 de noviembre, solo en cines", "Beta Fiction Spain", "PT30S", "2026-11-10", "0:30"),
    "ORXNiBTK5rc": ("El Director · Tráiler presentado por David Jiménez", "El Director - David Jiménez", "PT1M7S", "2026-11-16", "1:07"),
    "CgmhIDMm-B4": ("David Verdaguer presenta El director en Europa FM", "Europa FM", "PT15M50S", "2026-11-13", "15:50"),
}

def video(vid, miniatura=None):
    titulo, canal, _, _, dur = VIDEOS[vid]
    img = (f'<img src="{{r}}assets/img/{miniatura}" alt="" width="1280" height="720" loading="lazy" decoding="async">' if miniatura
           else f'<img src="https://i.ytimg.com/vi/{vid}/hqdefault.jpg" alt="" width="480" height="360" loading="lazy">')
    return (f'<div class="video"><button type="button" data-video="{vid}" data-titulo="{titulo}" aria-label="Reproducir: {titulo}">'
            f'{img}'
            f'<span class="play" aria-hidden="true"></span><span class="rotulo">{titulo}<small>{canal} · {dur}</small></span></button></div>')

def video_ld(vid):
    titulo, canal, dur, fecha, _ = VIDEOS[vid]
    return {"@type": "VideoObject", "name": titulo, "description": f"{titulo}. Publicado por {canal} en YouTube.",
            "thumbnailUrl": f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg", "uploadDate": fecha, "duration": dur,
            "embedUrl": f"https://www.youtube-nocookie.com/embed/{vid}", "contentUrl": f"https://www.youtube.com/watch?v={vid}"}

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
    "dossier": ("Beta Fiction Spain: kit y dossier de prensa oficial", "https://app.box.com/s/623pqrgihzm72b9biwaaolbqvacb66lb"),
    "publico_cardenal": ("Público: Fernández-Galiano, «El Cardenal»", "https://www.publico.es/economia/fernandez-galiano-cardenal-papel-queria-dominar-mundo.html"),
    "siglo_cardenal": ("El Siglo de Europa: el despido de Fernández-Galiano", "https://elsiglodeuropa.es/el-despido-de-fernandez-galiano-abre-una-nueva-epoca-en-el-mundo/"),
}

def fuentes(*claves, horizontal=False):
    items = "".join(f'<li><a href="{F[k][1]}" rel="noopener">{F[k][0]}</a></li>' for k in claves)
    clase = "fuentes horizontal" if horizontal else "fuentes"
    return f'<aside class="{clase}" aria-label="Fuentes"><p class="actualizado">Actualizado el {ACTUALIZADO_TXT}</p><p>Fuentes:</p><ul>{items}</ul><p>¿Ves un error? <a href="{{r}}metodologia-y-fuentes/#rectificaciones">Pide una rectificación</a>.</p></aside>'

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
    "publisher": {"@type": "Organization", "name": "Libros del K.O.", "url": LIBROSDELKO},
    "datePublished": "2019-04-08", "inLanguage": "es", "isbn": "9788417678081", "numberOfPages": 328,
    "genre": "No ficción",
}
PELI_LD = {
    "@type": "Movie", "@id": SITE + "pelicula/#pelicula", "name": "El director",
    "director": {"@type": "Person", "name": "Dani de la Orden"},
    "dateCreated": "2026", "datePublished": "2026-11-20", "inLanguage": "es", "countryOfOrigin": "ES",
    "genre": ["Thriller"],
    "duration": "PT1H55M",
    "image": SITE + "assets/img/cartel-el-director.jpg",
    "isBasedOn": {"@id": SITE + "libro/#libro"},
    "actor": [{"@type": "Person", "name": n} for n in [
        "David Verdaguer", "Alberto San Juan", "Fernando Colomo", "Xavi Sáez", "Miriam Iscla", "Joan Carreras",
        "Carmen Machi", "Emma Vilarasau", "Guillermo Toledo", "Fernando Cayo"]],
    "productionCompany": [{"@type": "Organization", "name": n} for n in [
        "Beta Fiction Spain", "Sábado Time", "Cardinal Content", "Historias de un Director SL"]],
}

# ---------- Enlaces a la primera mención de figuras públicas y empresas ----------
# Solo páginas verificadas de Wikipedia (o web oficial si no hay). No se enlaza a nadie
# asociado a apodos sin confirmar. Antonio Fernández-Galiano no se enlaza: la página de
# Wikipedia con ese nombre es de otra persona.
WIKI = "https://es.wikipedia.org/wiki/"
ENLACES = [
    ("El Mundo", WIKI + "El_Mundo_(Espa%C3%B1a)"),
    ("Libros del K.O.", LIBROSDELKO),
    ("Beta Fiction Spain", "https://betafiction.es/"),
    ("Pedro J. Ramírez", WIKI + "Pedro_J._Ram%C3%ADrez"),
    ("Casimiro García-Abadillo", WIKI + "Casimiro_Garc%C3%ADa-Abadillo"),
    ("Pedro García Cuartango", WIKI + "Pedro_Garc%C3%ADa_Cuartango"),
    ("César Alierta", WIKI + "C%C3%A9sar_Alierta"),
    ("Florentino Pérez", WIKI + "Florentino_P%C3%A9rez"),
    ("Unidad Editorial", WIKI + "Unidad_Editorial"),
    ("The New York Times", WIKI + "The_New_York_Times"),
    ("HBO Max", WIKI + "HBO_Max"),
    ("RTVE", WIKI + "RTVE"),
    ("3Cat", WIKI + "3Cat"),
]
# Perfiles de Wikipedia de personas con ficha o tarjeta propia en la web.
# En el texto se enlazan a su ficha interna; Wikipedia solo aparece como «Ver su perfil en Wikipedia».
WIKI_PERSONAS = {
    "David Jiménez": WIKI + "David_Jim%C3%A9nez_Garc%C3%ADa",
    "Dani de la Orden": WIKI + "Dani_de_la_Orden",
    "David Verdaguer": WIKI + "David_Verdaguer",
    "Alberto San Juan": WIKI + "Alberto_San_Juan",
    "Fernando Colomo": WIKI + "Fernando_Colomo",
    "Carmen Machi": WIKI + "Carmen_Machi",
    "Emma Vilarasau": WIKI + "Emma_Vilarasau",
    "Guillermo Toledo": WIKI + "Willy_Toledo",
    "Fernando Cayo": WIKI + "Fernando_Cayo",
    "Nacho Fresneda": WIKI + "Nacho_Fresneda",
    "Pau Durà": WIKI + "Pau_Dur%C3%A0",
}

def enlaces_internos():
    """Personas que se enlazan dentro del sitio (más tiempo de permanencia): ficha propia o tarjeta del reparto."""
    d = {"David Jiménez": "personajes/david-jimenez/", "Antonio Fernández-Galiano": "personajes/cardenal/",
         "Dani de la Orden": "pelicula/#dani-de-la-orden"}
    for _, actor, img, _ in REPARTO:
        d.setdefault(actor, f"pelicula/#actor-{img}")
    return d

def wiki_link(nombre, texto="Ver su perfil en Wikipedia"):
    u = WIKI_PERSONAS.get(nombre)
    return f'<a class="wiki" href="{u}" rel="noopener">{texto}</a>' if u else ""

# Nombres que se enlazan en todas sus menciones, no solo en la primera de cada página
ENLAZAR_SIEMPRE = {"Libros del K.O."}
_NO_ENLAZAR = {"small", "a", "h1", "h2", "h3", "button", "script", "figcaption", "dt", "time", "caption", "th", "nav", "title", "summary"}

def enlazar(html_txt, r="", ruta=""):
    import re
    partes = re.split(r"(<[^>]+>)", html_txt)
    pila = []
    hechos = set()
    for i, trozo in enumerate(partes):
        if trozo.startswith("<"):
            m = re.match(r"<(/?)([a-zA-Z0-9]+)", trozo)
            if m and m.group(2).lower() in _NO_ENLAZAR and not trozo.endswith("/>"):
                if m.group(1):
                    if pila: pila.pop()
                else:
                    pila.append(m.group(2).lower())
            continue
        if pila or not trozo.strip():
            continue
        salida = ""
        while True:
            mejor = None
            for nombre, url in ENLACES + INTERNOS:
                if nombre in hechos:
                    continue
                mm = re.search(r"(?<![\\wÁÉÍÓÚáéíóúñÑ])" + re.escape(nombre) + r"(?![\\wÁÉÍÓÚáéíóúñÑ])", trozo)
                if mm and (mejor is None or mm.start() < mejor[0].start()):
                    mejor = (mm, nombre, url)
            if not mejor:
                break
            mm, nombre, url = mejor
            if url.startswith(("http://", "https://")):
                salida += trozo[:mm.start()] + f'<a class="ref" href="{url}" rel="noopener">{nombre}</a>'
            elif url.split("#")[0] == ruta:
                salida += trozo[:mm.start()] + nombre   # no se enlaza a la misma página
            else:
                salida += trozo[:mm.start()] + f'<a class="ref interno" href="{r}{url}">{nombre}</a>'
            trozo = trozo[mm.end():]
            if nombre not in ENLAZAR_SIEMPRE:
                hechos.add(nombre)
        trozo = salida + trozo
        partes[i] = trozo
    return "".join(partes)

def externos_nueva_pestana(html_txt):
    """Los enlaces que salen de la web se abren en una pestaña nueva (target=_blank, rel=noopener)."""
    import re
    def ajustar(m):
        etiqueta = m.group(0)
        href = re.search(r'href="([^"]+)"', etiqueta).group(1)
        if not href.startswith(("http://", "https://")) or href.startswith(SITE) or "target=" in etiqueta:
            return etiqueta
        rel = re.search(r'rel="([^"]*)"', etiqueta)
        if rel:
            valores = rel.group(1).split()
            for v in ("noopener", "noreferrer"):
                if v not in valores: valores.append(v)
            etiqueta = etiqueta.replace(rel.group(0), f'rel="{" ".join(valores)}"')
        else:
            etiqueta = etiqueta[:-1] + ' rel="noopener noreferrer">'
        return etiqueta[:-1] + ' target="_blank">'
    return re.sub(r'<a\s[^>]*href="[^"]+"[^>]*>', ajustar, html_txt)

def plantilla(ruta, titulo, descripcion, cuerpo, ld=None, activo=None, portada=False, hero=False):
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
    cuerpo = enlazar(cuerpo.replace("{r}", r), r, ruta)
    return externos_nueva_pestana(f"""<!doctype html>
<html lang="es"{f' data-ga="{GA_ID}"' if GA_ID else ""}>
<head>
<meta charset="utf-8">
<script>document.documentElement.classList.add("js")</script>
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
<meta property="og:image" content="{SITE}assets/img/og-el-director.jpg">
<meta property="og:image:type" content="image/jpeg">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="El Director. Del libro a la película">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{SITE}assets/img/og-el-director.jpg">
<link rel="icon" href="{r}assets/img/favicon-48.png" sizes="48x48" type="image/png">
<link rel="icon" href="{r}assets/img/favicon-192.png" sizes="192x192" type="image/png">
<link rel="apple-touch-icon" href="{r}assets/img/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=UnifrakturCook:wght@700&family=Anton&family=Oswald:wght@400;500;600;700&display=swap">
<link rel="stylesheet" href="{r}assets/estilos.css?v={VERSION}">
<script type="application/ld+json">{json.dumps(grafo, ensure_ascii=False)}</script>
<script src="{r}assets/video.js?v={VERSION}" defer></script>
<script src="{r}assets/slider.js?v={VERSION}" defer></script>
<script src="{r}assets/encuesta.js?v={VERSION}" defer></script>
<script src="{r}assets/cookies.js?v={VERSION}" defer></script>
</head>
<body{' class="es-portada"' if portada else (' class="con-hero"' if hero else '')}>
<a class="salto" href="#contenido">Saltar al contenido</a>
<div class="arriba">
<div class="cinta">En cines desde el 20 de noviembre de 2026 · <a href="{r}metodologia-y-fuentes/">Web informativa e independiente</a></div>
<header class="sitio">
  <div class="contenedor">
    <a class="marca" href="{r}"><img src="{r}assets/img/portada/logo-web.png" alt="El Director" width="172" height="36"><span>Del libro a la película</span></a>
    <button type="button" class="menu-boton" aria-expanded="false" aria-controls="menu-principal"><span class="menu-icono" aria-hidden="true"></span><span class="menu-texto">Menú</span></button>
    <nav id="menu-principal" aria-label="Principal"><ul class="menu">{menu}</ul></nav>
  </div>
</header>
</div>
<main id="contenido"{' class="sin-relleno"' if portada else (' class="con-hero"' if hero else '')}>
{cuerpo}
</main>
<footer class="pie">
  <div class="contenedor">
    <p class="pie-marca"><img class="pie-logo" src="{r}assets/img/portada/logo-web.png" alt="El Director" width="258" height="54" loading="lazy"><span>Del libro a la película</span></p>
    <div class="pie-columnas">
      <section>
        <h2>Web independiente</h2>
        <p>Proyecto informativo y personal. No es la web oficial del libro, de la película ni de su autor, y no tiene relación con <a href="{LIBROSDELKO}">Libros del K.O.</a>, Beta Fiction Spain ni David Jiménez.</p>
      </section>
      <section>
        <h2>Con fuentes</h2>
        <p>Cada relación entre personas reales y personajes enlaza sus fuentes e indica su grado de certeza. La película es una ficción inspirada en hechos reales.</p>
      </section>
      <section>
        <h2>No monetizada</h2>
        <p>Sin publicidad. Google Analytics solo se activa si lo aceptas, y los vídeos solo se cargan si pulsas reproducir. Imágenes: <a href="{r}metodologia-y-fuentes/#creditos">créditos</a>.</p>
      </section>
    </div>
    <hr>
    <nav aria-label="Pie de página">
      <ul class="pie-menu">
        <li><a href="{r}personajes/david-jimenez/">David Jiménez</a></li>
        <li><a href="{r}metodologia-y-fuentes/">Metodología y aviso legal</a></li>
        <li><a href="{r}metodologia-y-fuentes/#rectificaciones">Rectificaciones</a></li>
        {'<li><a href="#" data-abrir-cookies>Preferencias de cookies</a></li>' if GA_ID else ''}
      </ul>
    </nav>
  </div>
</footer>
<a class="volver-arriba" href="#contenido" aria-label="Volver arriba"></a>
{AVISO_COOKIES.replace("{r}", r) if GA_ID else ""}
</body>
</html>
""")

AVISO_COOKIES = """<div id="aviso-cookies" class="aviso-cookies" role="dialog" aria-live="polite" aria-label="Aviso de cookies" hidden>
  <p><strong>¿Nos dejas medir las visitas?</strong> Usamos Google Analytics para saber cuánta gente visita la web y qué páginas lee. Solo se activa si aceptas. <a href="{r}metodologia-y-fuentes/#cookies">Más información</a>.</p>
  <div class="aviso-cookies-botones"><button type="button" class="btn" data-cookies="si">Aceptar</button><button type="button" class="btn sec" data-cookies="no">Rechazar</button></div>
</div>"""

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

# Reparto según el dossier de prensa oficial: (personaje, actor, foto, colaboración especial)
REPARTO = [
    ("David", "David Verdaguer", "david", False),
    ("Cardenal", "Alberto San Juan", "cardenal", False),
    ("Fernando", "Fernando Colomo", "fernando", False),
    ("Julio", "Joan Carreras", "julio", False),
    ("Elena", "Anna Alarcón", "elena", False),
    ("Oskar", "David Vert", "oskar", False),
    ("Sara", "Miriam Iscla", "sara", False),
    ("Pedro", "Pau Durà", "pedro", False),
    ("Virginia", "Anna Sahun Martí", "virginia", False),
    ("Marina", "Mia Sala-Patau", "marina", False),
    ("Ortega", "Marc Rodríguez", "ortega", False),
    ("Aurelio Ortiz", "Xavi Sáez", "aurelio-ortiz", False),
    ("Tesorero", "Nacho Fresneda", "tesorero", False),
    ("Julia", "Emma Vilarasau", "julia", True),
    ("Vidal", "Guillermo Toledo", "vidal", True),
    ("Vicepresidenta", "Carmen Machi", "vicepresidenta", True),
    ("Ministro", "Fernando Cayo", "ministro", True),
]
INSPIRADO = {"David": ("personajes/david-jimenez/", "David Jiménez"), "Cardenal": ("personajes/cardenal/", "Antonio Fernández-Galiano")}
INTERNOS = list(enlaces_internos().items())

def tarjetas_reparto():
    t = []
    for pers, actor, img, esp in REPARTO:
        extra = '<span class="especial">Colaboración especial</span>' if esp else ""
        insp = INSPIRADO.get(pers)
        insp_txt = f'<a class="inspira" href="{{r}}{insp[0]}">Inspirado en {insp[1]}</a>' if insp else '<span class="inspira pend">Persona real: pendiente</span>'
        w = wiki_link(actor, "Wikipedia")
        t.append(f'<li class="actor-tarjeta" id="actor-{img}"><img src="{{r}}assets/img/reparto/{img}.jpg" alt="{actor} como {pers}" width="360" height="360" loading="lazy" decoding="async">'
                 f'{extra}<span class="pers">{pers}</span><strong>{actor}</strong>{insp_txt}{w}</li>')
    return '<ul class="reparto-grid">' + "".join(t) + "</ul>"

def filas_reparto():
    filas = []
    for pe, a, _, e in REPARTO:
        esp = " <small>(colaboración especial)</small>" if e else ""
        if pe in INSPIRADO:
            real = '<a href="{r}' + INSPIRADO[pe][0] + '">' + INSPIRADO[pe][1] + '</a>'
            sello = '<span class="sello s-conf">Confirmado</span>'
        else:
            real = "Pendiente"
            sello = '<span class="sello s-pend">Pendiente</span>'
        filas.append(f"<tr><td>{a}{esp}</td><td>{pe}</td><td>{real}</td><td>{sello}</td></tr>")
    return "".join(filas)

FOTOGRAMAS = 6

HITOS = [
    ("1998", "Jiménez abre en Hong Kong la primera delegación de <i>El Mundo</i> en Asia."),
    ("2014", "Pedro J. Ramírez deja la dirección del periódico. Le sustituye Casimiro García-Abadillo."),
    ("2015", "El 30 de abril, Jiménez es nombrado director a propuesta de Antonio Fernández-Galiano."),
    ("2016", "El 25 de mayo deja la dirección tras su despido. Le sucede Pedro García Cuartango."),
    ("2019", "Libros del K.O. publica <i>El director</i>."),
    ("2025", "Beta Fiction adquiere los derechos de adaptación."),
    ("2026", "Rodaje en febrero, teaser en julio y estreno en cines el 20 de noviembre."),
]

# ---------------- PORTADA ----------------
# ---------- Slider "Vida real, libro y película" ----------
# (imagen, alt, enlace, tono, [(lado, blanco, amarillo), ...], posición del foco en móvil)
SLIDES = [
    ("slide-1-v2.jpg", "Silueta en lugar de Antonio Fernández-Galiano, del que no hay foto con licencia libre, en una reunión", "personajes/cardenal/", "",
     [("izq", "Antonio Fernández-Galiano", "En el libro “El Cardenal”")], "50%"),
    ("slide-2.jpg", "Alberto San Juan como Cardenal en El Director", "personajes/cardenal/", "",
     [("der", "Cardenal", "Alberto San Juan")], "50%"),
    ("slide-3.jpg", "David Jiménez en 2019", "personajes/david-jimenez/", "claro",
     [("der", "David Jiménez", "En el libro: el narrador")], "28%"),
    ("slide-4.jpg", "David Verdaguer como David Jiménez en El Director", "personajes/david-jimenez/", "",
     [("izq", "David Verdaguer", "David Jiménez")], "58%"),
    ("slide-5-fondo.jpg", "Redacción de la película con dos siluetas: personajes del libro aún sin identificar", "encuesta/", "",
     [("izq", "La Digna, El Señorito, Rasputín…", "Apodos del libro"), ("der", "Ayúdanos a descubrirlos", "Participa en nuestra encuesta")], "50%",
     [("slide-5-mujer-v2.png", "entra-izq"), ("slide-5-hombre-v2.png", "entra-der")]),
]

def slide(img, alt, enlace, tono, textos, foco, capas=()):
    t = "".join(f'<a class="vrlp-texto {lado}" href="{{r}}{enlace}"><strong>{b}</strong><span>{am}</span></a>' for lado, b, am in textos)
    foto = f'<img src="{{r}}assets/img/slider/{img}" alt="{alt}" width="2000" height="741" decoding="async">'
    if capas:
        # Siluetas en capas sueltas (lienzo 2000x741 transparente) para poder animarlas.
        c = "".join(f'<img class="vrlp-capa {clase}" src="{{r}}assets/img/slider/{png}" alt="" width="2000" height="741" decoding="async">' for png, clase in capas)
        foto = f'<div class="vrlp-lienzo">{foto}{c}</div>'
    return f'<figure class="vrlp-slide" data-tono="{tono}" style="--foco:{foco}">{foto}{t}</figure>'


PAGINAS[""] = dict(
    titulo="El Director: quién es quién del libro a la película",
    desc="Qué persona real hay detrás de cada personaje de El Director, el libro de David Jiménez y la película de Dani de la Orden. Con fuentes y grado de certeza.",
    cuerpo=f"""
<section class="hero hero-v3">
  <img class="hero-fondo" src="{{r}}assets/img/portada/hero-butacas.jpg" alt="" width="1920" height="1079" fetchpriority="high" decoding="async">
  <div class="contenedor hero-texto">
    <div class="hero-firmas"><small>David Jiménez (2019)</small><small>Dani de la Orden (2026)</small></div>
    <h1><img src="{{r}}assets/img/portada/logo-web.png" alt="El Director" width="860" height="181"><span class="sub-v3">Del libro a la película</span></h1>
    <p class="entradilla">En 2015, David Jiménez dejó de ser corresponsal de guerra para dirigir <i>El Mundo</i>. <strong>Duró un año.</strong> Lo contó todo en un libro. Ahora llega al cine. Aquí te contamos <strong>quién es quién</strong>.</p>
    <div class="flechas">
      <a href="{{r}}personajes/">Ver quién es quién</a>
      <a href="{{r}}pelicula/#donde-ver">Dónde ver la película</a>
      <a href="{{r}}libro/#donde-leer">Dónde leer el libro</a>
    </div>
  </div>
</section>

<section class="vrlp" aria-roledescription="carrusel" aria-labelledby="h-vrlp">
  <h2 class="vrlp-titulo" id="h-vrlp"><a href="{{r}}encuesta/" tabindex="-1">Vida real,<br> libro y película</a></h2>
  <div class="vrlp-slides">
    {"".join(slide(*d) for d in SLIDES)}
  </div>
  <button type="button" class="vrlp-flecha ant" aria-label="Anterior"></button>
  <button type="button" class="vrlp-flecha sig" aria-label="Siguiente"></button>
  <div class="vrlp-control">
    <button type="button" class="vrlp-pausa" aria-label="Pausar">❚❚</button>
    {"".join(f'<button type="button" class="vrlp-punto" aria-label="Ver {i + 1} de {len(SLIDES)}"></button>' for i in range(len(SLIDES)))}
  </div>
</section>
<div class="faldon"><div class="contenedor"><p><span class="sello s-conf">Confirmado</span> Solo mostramos como confirmadas las relaciones que publican el autor, la productora o varios medios. Las siluetas sustituyen a personas reales de las que no hay foto con licencia libre. <a href="{{r}}metodologia-y-fuentes/">Cómo trabajamos</a>.</p></div></div>

<section class="banda-foto teaser-v3" aria-labelledby="h-teaser">
  <img class="banda-fondo" src="{{r}}assets/img/portada/fondo-edificios.jpg" alt="" width="1920" height="1080" loading="lazy" decoding="async">
  <div class="contenedor">
    <h2 id="h-teaser">El teaser</h2>
    {video("PUQzmris2CE", "portada/teaser.jpg")}
  </div>
</section>

<section class="banda-foto peli-v3 obras-v3" aria-label="El libro y la película">
  <img class="banda-fondo" src="{{r}}assets/img/portada/fondo-exterior.jpg" alt="" width="1920" height="1082" loading="lazy" decoding="async">
  <div class="contenedor">
    <div class="volteo" data-cara="libro">
      <div class="volteo-carta">
        <figure class="cara cara-libro"><img src="{{r}}assets/img/portada/libro-el-director.jpg" alt="Cubierta del libro El director, de David Jiménez (Libros del K.O.)" width="780" height="1200" loading="lazy" decoding="async"></figure>
        <figure class="cara cara-peli"><img src="{{r}}assets/img/cartel-el-director.jpg" alt="Cartel oficial de la película El Director" width="560" height="800" loading="lazy" decoding="async"></figure>
      </div>
    </div>
    <div class="obras-textos">
      <div class="peli-texto obra-panel" data-cara="libro">
        <h2>El libro</h2>
        <p class="peli-entrada"><i>El director</i> (Libros del K.O., 2019) relata el año de Jiménez al frente de <i>El Mundo</i> y el sistema de pactos entre prensa, empresas y política que él llama “Los Acuerdos”.</p>
        <dl class="datos"><dt>Autor</dt><dd>David Jiménez</dd><dt>Editorial</dt><dd>Libros del K.O.</dd><dt>Páginas</dt><dd>328</dd></dl>
        <div class="flechas"><a href="{{r}}libro/">Sobre el libro</a><a href="{{r}}libro/#donde-leer">Dónde adquirirlo</a></div>
      </div>
      <div class="peli-texto obra-panel" data-cara="peli">
        <h2>La película</h2>
        <p class="peli-entrada">Thriller de Dani de la Orden con David Verdaguer y Alberto San Juan, con guion de Alejandro Hernández y Michel Gaztambide. En cines desde el 20 de noviembre de 2026.</p>
        <dl class="datos"><dt>Dirección</dt><dd>Dani de la Orden</dd><dt>Reparto</dt><dd>David Verdaguer, Alberto San Juan, Fernando Colomo, Carmen Machi…</dd><dt>Duración</dt><dd>1 h 55 min</dd><dt>Distribución</dt><dd>Beta Fiction Spain</dd></dl>
        <div class="flechas"><a href="{{r}}pelicula/">Ficha y reparto</a><a href="{{r}}pelicula/#donde-ver">Dónde verla</a></div>
      </div>
      <div class="volteo-control" role="group" aria-label="Elegir libro o película">
        <button type="button" data-ir="libro">El libro</button><button type="button" data-ir="peli">La película</button>
      </div>
    </div>
  </div>
</section>
""",
    ld=[LIBRO_LD, PELI_LD, video_ld("PUQzmris2CE")], portada=True,
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
<p class="entradilla">David Jiménez escribió su libro con dos reglas: los políticos, empresarios y miembros de la monarquía aparecen con nombre y apellidos; los periodistas y directivos del diario, con apodos. La película cambia algunos nombres más: según el dossier de prensa oficial, salvo David, los personajes llevan nombres de ficción o un cargo, como el Ministro o la Vicepresidenta.</p>
<p>Cada fila lleva un sello:</p>
<ul class="leyenda-sellos">
<li><span class="sello s-conf">Confirmado</span> cuando lo publican el autor, la productora o varios medios.</li>
<li><span class="sello s-real">Nombre real</span> cuando la persona aparece con su nombre en el libro.</li>
<li><span class="sello s-pend">Pendiente</span> cuando aún no hay datos fiables.</li>
</ul>
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
<p>El libro usa apodos para la gente de la redacción y la dirección del diario: “La Digna”, “El Señorito”, “Rasputín”, “El Poeta”, “El Secretario”, “El Reportero”, “los inspirados” o “los de la segunda planta”, entre otros. Algunos medios han publicado a quién corresponden, pero todavía no tenemos fuentes suficientes para afirmarlo.</p>
<p>Ya conocemos el personaje de cada actor, porque lo publica el dossier de prensa oficial. Lo que aún no sabemos es en qué persona real se inspira cada uno, salvo David y Cardenal. No lo deduciremos por parecidos de nombre o de cargo: solo lo publicaremos cuando lo confirmen el autor, la productora o varios medios.</p>
</div>
<div class="tabla"><table>
<caption>Reparto y personajes según el dossier de prensa oficial</caption>
<thead><tr><th>Actor o actriz</th><th>Personaje</th><th>Persona real</th><th>Certeza</th></tr></thead>
<tbody>
{filas_reparto()}
</tbody></table></div>
{fuentes("dossier", "wiki_libro", "wiki_peli", "infobae", "cineconn", "cinemagavia", "ecartelera", "av451")}
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
<div class="careo">
  {silueta("Antonio Fernández-Galiano · vida real")}
  <div class="igual" aria-hidden="true">=</div>
  {foto_kit("reparto/cardenal.jpg", "Alberto San Juan como Cardenal", "Alberto San Juan · Cardenal")}
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
{fuentes("wiki_libro", "publico_cardenal", "siglo_cardenal", "infobae", "cineconn", "beta")}
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
<div class="careo">
  {foto("david-jimenez", "David Jiménez · vida real", carga="eager")}
  <div class="igual" aria-hidden="true">=</div>
  {foto_kit("reparto/david.jpg", "David Verdaguer como David Jiménez", "David Verdaguer · David Jiménez")}
</div>
<dl class="datos">
  <dt>En el libro</dt><dd>Narrador en primera persona</dd>
  <dt>En la película</dt><dd>David Jiménez</dd>
  <dt>Actor</dt><dd>David Verdaguer</dd>
  <dt>Director de El Mundo</dt><dd>30 de abril de 2015 – 25 de mayo de 2016</dd>
  <dt>Más información</dt><dd>{wiki_link("David Jiménez")}</dd>
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
<p>Mantiene un <a href="{YOUTUBE}" rel="noopener">canal de YouTube</a> con su nombre, dedicado a la actualidad política y mediática. Allí presentó el tráiler de la película días antes del estreno.</p>
</div>
{video("ORXNiBTK5rc")}
<div class="acciones"><a class="btn" href="{{r}}libro/#donde-leer">Dónde leer el libro</a><a class="btn sec" href="{{r}}pelicula/#donde-ver">Dónde ver la película</a></div>
{fuentes("wiki_autor", "wiki_libro", "wiki_peli", "youtube")}
{siguiente(("Ficha", "El Cardenal", "personajes/cardenal/"), ("Libro", "El director (2019)", "libro/"), ("Contexto", "La historia real", "historia-real/"))}
</div>""",
    ld=[ld_migas([("Inicio", ""), ("Quién es quién", "personajes/"), ("David Jiménez", "personajes/david-jimenez/")]),
        {"@type": "Person", "@id": SITE + "personajes/david-jimenez/#persona", "name": "David Jiménez García",
         "birthDate": "1971-01-11", "birthPlace": "Barcelona", "jobTitle": "Periodista y escritor",
         "image": SITE + "assets/img/david-jimenez.jpg",
         "sameAs": [F["wiki_autor"][1], YOUTUBE]}, video_ld("ORXNiBTK5rc")],
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
    cuerpo=f"""<div class="banda" style="margin-top:-40px"><div class="contenedor"><p class="antetitulo" style="color:var(--papel)">20 de noviembre · solo en cines</p></div></div>
<div class="contenedor" style="margin-top:28px">
{migas(("Inicio", ""), ("La película", None))}
<p class="antetitulo">La película · Estreno el 20 de noviembre de 2026</p>
<h1><span class="el">El</span> director <span style="font-size:.45em;display:block;letter-spacing:.14em;color:var(--oro);margin-top:8px">La verdad tiene un precio</span></h1>
<div class="lectura">
<p class="entradilla">Un corresponsal con más de veinte años cubriendo guerras es nombrado director de uno de los principales diarios del país. Su defensa del periodismo riguroso choca desde el principio con los intereses ocultos del periódico, protegidos por Cardenal, el editor.</p>
</div>
<div class="ficha-peli">
<figure class="cubierta cartel-oficial"><img src="{{r}}assets/img/cartel-el-director.jpg" alt="Cartel oficial de El Director" width="560" height="800" decoding="async"></figure>
<dl class="datos">
  <dt>Dirección</dt><dd>Dani de la Orden</dd>
  <dt>Guion</dt><dd>Alejandro Hernández y Michel Gaztambide, sobre el libro de David Jiménez</dd>
  <dt>Fotografía</dt><dd>Maria Codina</dd>
  <dt>Música</dt><dd>Maria Chiara Casà</dd>
  <dt>Producción</dt><dd>Beta Fiction Spain, Sábado Time, Cardinal Content e Historias de un Director SL, con la participación de HBO Max, RTVE y 3Cat</dd>
  <dt>Distribución</dt><dd>Beta Fiction Spain</dd>
  <dt>Género</dt><dd>Thriller periodístico</dd>
  <dt>Duración</dt><dd>1 h 55 min</dd>
  <dt>Estreno</dt><dd>20 de noviembre de 2026, en cines</dd>
</dl>
</div>
<h2>Teaser y avances</h2>
{video("PUQzmris2CE")}
<div class="videos" style="margin-top:22px">
  <div>{video("NT7O8rzR3PU")}</div>
  <div>{video("CgmhIDMm-B4")}</div>
</div>
<h2>Reparto y personajes</h2>
<p class="nota">Personajes y fotos según el dossier de prensa oficial de la película.</p>
{tarjetas_reparto()}
<h2>Fotogramas</h2>
<div class="fotogramas">{"".join(f'<img src="{{r}}assets/img/fotogramas/fotograma-{n}.jpg" alt="Fotograma de El Director" width="1100" height="618" loading="lazy" decoding="async">' for n in range(1, FOTOGRAMAS + 1))}</div>
<div class="careo" id="dani-de-la-orden" style="grid-template-columns:minmax(0,180px) minmax(0,1fr);max-width:640px">
  {foto("dani-de-la-orden", "Dani de la Orden · director")}
  <p class="nota" style="margin:0">Director de <i>Barcelona, noche de verano</i> y <i>Litus</i>.<br>{wiki_link("Dani de la Orden")}</p>
</div>
<div class="lectura">
<h2>Cómo se ve</h2>
<p>La crítica destaca una fotografía de luz fría y planos muy abiertos que aíslan al protagonista en salas de reuniones, el uso de imágenes de archivo de informativos y un ritmo de thriller. El proyecto nació como serie antes de convertirse en película.</p>
<h2 id="donde-ver">Dónde ver la película</h2>
<p>En cines desde el 20 de noviembre. Enlaces informativos, sin afiliación.</p>
</div>
{DONDE_VER}
{fuentes("dossier", "beta", "av451", "wiki_peli", "infobae", "cineconn", "cinemagavia", "ecartelera")}
{siguiente(("Tabla", "Quién es quién", "personajes/"), ("Libro", "El director (2019)", "libro/"), ("Contexto", "La historia real", "historia-real/"))}
</div>""",
    ld=[ld_migas([("Inicio", ""), ("La película", "pelicula/")]), PELI_LD, video_ld("PUQzmris2CE"), video_ld("NT7O8rzR3PU"), video_ld("CgmhIDMm-B4")],
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
    ("¿Qué personajes hay en El Director?", "Según el dossier de prensa oficial: David (David Verdaguer), Cardenal (Alberto San Juan), Fernando (Fernando Colomo), Julio (Joan Carreras), Elena (Anna Alarcón), Oskar (David Vert), Sara (Miriam Iscla), Pedro (Pau Durà), Virginia (Anna Sahun Martí), Marina (Mia Sala-Patau), Ortega (Marc Rodríguez), Aurelio Ortiz (Xavi Sáez) y el Tesorero (Nacho Fresneda). Con la colaboración especial de Emma Vilarasau (Julia), Guillermo Toledo (Vidal), Carmen Machi (la Vicepresidenta) y Fernando Cayo (el Ministro)."),
    ("¿Cuánto dura El Director?", "1 hora y 55 minutos."),
    ("¿Cuándo se estrena El Director?", "El 20 de noviembre de 2026 en cines de España, según el cartel oficial y la distribuidora. Algunos medios publicaron el 27 de noviembre."),
    ("¿Quién dirige la película?", "Dani de la Orden, con guion de Alejandro Hernández y Michel Gaztambide."),
    ("¿Qué periódico es el de El Director?", "El libro trata de El Mundo, el diario que Jiménez dirigió. En la película se presenta como un importante diario nacional."),
    ("¿Qué son “Los Acuerdos”?", "Es el nombre que Jiménez da al sistema de pactos y favores entre el poder económico, el político y la prensa que describe en el libro."),
    ("¿Quiénes son La Digna, El Señorito o Rasputín?", "Son apodos que Jiménez usa en el libro para periodistas y directivos del periódico. Aún no tenemos fuentes suficientes para confirmar a quién corresponden ni su personaje en la película."),
    ("¿Es esta la web oficial?", "No. Es un proyecto informativo e independiente, no monetizado."),
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
{fuentes("wiki_libro", "wiki_peli", "beta", "av451", "infobae", horizontal=True)}
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
<p>“El Director. Del libro a la película” es un proyecto independiente con fines informativos. No es la web oficial del libro, de la película ni de su autor, y no está vinculado a Libros del K.O., Beta Fiction Spain ni David Jiménez. Es una web no monetizada: no tiene publicidad y no recibe dinero de nadie. Solo mide las visitas con Google Analytics si lo aceptas (ver «Cookies y medición»). Los enlaces a librerías y cines son solo informativos.</p>
<h2>Cómo verificamos</h2>
<ul>
<li><span class="sello s-conf">Confirmado</span> Lo publican el autor, la productora o la distribuidora, o al menos dos medios independientes.</li>
<li><span class="sello s-real">Nombre real</span> La persona aparece con su nombre en el libro, según fuentes publicadas.</li>
<li><span class="sello s-pend">Pendiente</span> No hay fuentes suficientes. No asociamos a ninguna persona real con un apodo o un personaje hasta tenerlas.</li>
</ul>
<p>Recogemos lo que ya han publicado el autor y otros medios, enlazamos las fuentes en cada página e indicamos la fecha de actualización. No emitimos juicios sobre las personas mencionadas. La película es una obra de ficción inspirada en hechos reales.</p>
<h2 id="imagenes">Imágenes y vídeos</h2>
<p>Solo usamos fotografías con licencia libre (Creative Commons o dominio público). Para no recargar las páginas, el autor y la licencia de cada imagen se recogen en el listado de créditos de esta página. Las mostramos recortadas y en duotono; las fotos de personas reales se presentan separadas de las de los actores. Si no hay una foto libre de una persona, usamos una silueta.</p>
<p>El cartel, las fotos del reparto y los fotogramas proceden del kit de prensa público de Beta Fiction Spain y se usan con fines informativos, citando su procedencia. La cubierta del libro es de Libros del K.O. y se muestra solo para identificar la obra. Las ilustraciones de papel triturado, butacas y siluetas son propias.</p>
<p>Los vídeos son publicaciones públicas de YouTube incrustadas desde el modo de privacidad mejorada (youtube-nocookie.com). El reproductor y sus cookies solo se cargan si pulsas reproducir; hasta entonces solo se muestra la miniatura, servida por YouTube.</p>
<p>Las marcas y títulos citados pertenecen a sus titulares.</p>
<h2 id="creditos">Créditos de las imágenes</h2>
</div>
<div class="tabla"><table>
<caption>Todas las imágenes de terceros que usa la web</caption>
<thead><tr><th>Imagen</th><th>Dónde aparece</th><th>Autor y fuente</th><th>Licencia</th><th>Cambios</th></tr></thead>
<tbody>
<tr><td>Fotogramas del slider “Vida real, libro y película” (Cardenal, David, redacción)</td><td>Portada</td><td><a href="https://app.box.com/s/623pqrgihzm72b9biwaaolbqvacb66lb" rel="noopener">Beta Fiction Spain, material promocional</a></td><td>Material de prensa</td><td>Recortados; con siluetas propias superpuestas en lugar de personas sin foto libre</td></tr>
<tr><td>Fotogramas de fondo (patio de butacas, edificios, exterior) y miniatura del teaser</td><td>Portada e imagen para redes sociales</td><td><a href="https://app.box.com/s/623pqrgihzm72b9biwaaolbqvacb66lb" rel="noopener">Beta Fiction Spain, material promocional</a></td><td>Material de prensa</td><td>Redimensionados y oscurecidos</td></tr>
{"".join(f'<tr><td>{v[0]}</td><td>{DONDE_FOTO[k]}</td><td><a href="{v[4]}" rel="noopener">{v[1]}</a> (Wikimedia Commons)</td><td><a href="{v[3]}" rel="noopener license">{v[2]}</a></td><td>Recortada; en la portada, con el fondo eliminado</td></tr>' for k, v in FOTOS.items())}
{"".join(f'<tr><td>{c[1]}</td><td>Portada, cartelera y cartel recreado</td><td><a href="{c[5]}" rel="noopener">{c[2]}</a></td><td><a href="{c[4]}" rel="noopener license">{c[3]}</a></td><td>Solo el contorno, rellenado con un color plano. No representa a ninguna persona concreta</td></tr>' for c in SILUETAS)}
<tr><td>Cubierta del libro</td><td>Portada</td><td><a href="https://www.librosdelko.com/" rel="noopener">Libros del K.O.</a></td><td>Material promocional de la editorial</td><td>Redimensionada</td></tr>
{"".join(f'<tr><td>{v["nombre"]}</td><td>Encuesta</td><td><a href="{v["pagina"]}" rel="noopener">{v["autor"]}</a> (Wikimedia Commons)</td><td>' + (f'<a href="{v["licencia_url"]}" rel="noopener license">{v["licencia"]}</a>' if v["licencia_url"] else v["licencia"]) + '</td><td>Recortada, en blanco y negro</td></tr>' for v in CREDITOS_LIBRO.values())}
<tr><td>Cartel oficial</td><td>Portada, película</td><td><a href="https://app.box.com/s/623pqrgihzm72b9biwaaolbqvacb66lb" rel="noopener">Beta Fiction Spain, kit de prensa</a></td><td>Material de prensa</td><td>Redimensionado</td></tr>
<tr><td>Fotos del reparto en su papel</td><td>Portada, fichas, película</td><td><a href="https://app.box.com/s/623pqrgihzm72b9biwaaolbqvacb66lb" rel="noopener">Beta Fiction Spain, dossier de prensa</a></td><td>Material de prensa</td><td>Recortadas; en la portada, con el fondo eliminado</td></tr>
<tr><td>Fotos de cabecera de las páginas interiores</td><td>Quién es quién, Cardenal, libro, película, historia real, preguntas, metodología, encuesta</td><td><a href="https://app.box.com/s/623pqrgihzm72b9biwaaolbqvacb66lb" rel="noopener">Lander Larrañaga / Beta Fiction Spain, kit de prensa</a></td><td>Material de prensa</td><td>Redimensionadas y oscurecidas con un degradado</td></tr>
<tr><td>Fotogramas</td><td>Película</td><td><a href="https://app.box.com/s/623pqrgihzm72b9biwaaolbqvacb66lb" rel="noopener">Lander Larrañaga / Beta Fiction Spain, kit de prensa</a></td><td>Material de prensa</td><td>Redimensionados</td></tr>
{"".join(f'<tr><td>Miniatura: {VIDEOS[v][0]}</td><td>{DONDE_VIDEO[v]}</td><td><a href="https://www.youtube.com/watch?v={v}" rel="noopener">{VIDEOS[v][1]}</a> (YouTube)</td><td>Inserción permitida por YouTube</td><td>Ninguno</td></tr>' for v in VIDEOS)}
</tbody></table></div>
<div class="lectura">
<p>Son ilustraciones propias, sin derechos de terceros: el papel triturado, el patio de butacas ilustrado y la silueta “sin foto”.</p>
<h2 id="cookies">Cookies y medición</h2>
<p>Para saber cuánta gente visita la web y qué páginas lee usamos Google Analytics 4. <strong>Solo se activa si lo aceptas</strong> en el aviso que aparece al entrar: si lo rechazas o no eliges, no se carga nada de Google. Analytics usa las cookies <span class="mono">_ga</span> y <span class="mono">_ga_*</span>, que duran hasta dos años, y Google recibe tu IP, que no se guarda completa. Los datos solo se usan para estadísticas de la web y no se cruzan con publicidad.</p>
<p>Tu elección se guarda en tu navegador y puedes cambiarla cuando quieras desde «Preferencias de cookies», en el pie de cada página. La encuesta no usa cookies: solo recuerda en tu navegador qué personajes has votado.</p>
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
<div class="acciones"><a class="btn" href="/">Ir a la portada</a><a class="btn sec" href="/personajes/">Ver quién es quién</a></div></div>"""

ICONO = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" fill="#0f2a2c"/><text x="32" y="46" font-family="Georgia,serif" font-size="40" font-weight="700" text-anchor="middle" fill="#e3b23c">D</text></svg>"""

# ---------- Encuesta "¿Quién es quién?" (modo prueba) ----------
SEXO_PELI = {"Elena": "m", "Sara": "m", "Virginia": "m", "Marina": "m", "Julia": "m", "Vicepresidenta": "m"}
# (id, nombre, tipo, sexo h/m/?, descripción, foto) · sexo "?" = el libro no lo deja claro: sale en las dos listas
LIBRO_ENCUESTA = [
    ("rajoy", "Mariano Rajoy", "real", "h", "Presidente del Gobierno (2011-2018)"),
    ("saenz-de-santamaria", "Soraya Sáenz de Santamaría", "real", "m", "Vicepresidenta del Gobierno (2011-2018)"),
    ("barcenas", "Luis Bárcenas", "real", "h", "Extesorero del Partido Popular"),
    ("villarejo", "José Manuel Villarejo", "real", "h", "Comisario de policía"),
    ("alierta", "César Alierta", "real", "h", "Presidente de Telefónica hasta 2016"),
    ("florentino-perez", "Florentino Pérez", "real", "h", "Presidente de ACS y del Real Madrid"),
    ("pedro-j-ramirez", "Pedro J. Ramírez", "real", "h", "Fundador y director de El Mundo hasta 2014"),
    ("garcia-abadillo", "Casimiro García-Abadillo", "real", "h", "Director de El Mundo (2014-2015)"),
    ("botin", "Emilio Botín", "real", "h", "Presidente del Banco Santander hasta 2014"),
    ("faine", "Isidro Fainé", "real", "h", "Presidente de La Caixa"),
    ("sanchez-galan", "Ignacio Sánchez Galán", "real", "h", "Presidente de Iberdrola"),
    ("francisco-gonzalez", "Francisco González", "real", "h", "Presidente del BBVA hasta 2018"),
    ("urdangarin", "Iñaki Urdangarin", "real", "h", "Cuñado del rey Felipe VI"),
    ("inda", "Eduardo Inda", "real", "h", "Periodista"),
    ("marhuenda", "Francisco Marhuenda", "real", "h", "Director de La Razón"),
    ("trinidad-jimenez", "Trinidad Jiménez", "real", "m", "Exministra, con cargo en Telefónica"),
    ("la-digna", "La Digna", "apodo", "m", "Apodo de alguien de la redacción"),
    ("la-favorita", "La Favorita", "apodo", "m", "Apodo de alguien de la redacción"),
    ("rasputin", "Rasputín", "apodo", "h", "Apodo de alguien de la redacción"),
    ("el-poeta", "El Poeta", "apodo", "h", "Apodo de alguien de la redacción"),
    ("el-senorito", "El Señorito", "apodo", "h", "Apodo de alguien de la redacción"),
    ("el-reportero", "El Reportero", "apodo", "h", "Apodo de alguien de la redacción"),
    ("el-secretario", "El Secretario", "apodo", "h", "Apodo de alguien de la redacción"),
    ("el-dos", "El Dos", "apodo", "h", "Apodo de alguien de la redacción"),
    ("el-viti", "El Viti", "apodo", "h", "Apodo de alguien de la redacción"),
    ("money", "Money", "apodo", "?", "Apodo de alguien de la redacción"),
    ("asuntos-internos", "Asuntos Internos", "apodo", "?", "Apodo de alguien de la redacción"),
    ("chupatintas", "Chupatintas", "apodo", "?", "Apodo de alguien de la redacción"),
    ("ninguno", "Ninguno", "ninguno", "*", "Creo que es un personaje creado para la película"),
]

def datos_encuesta():
    peli = [{"id": img, "nombre": pe, "actor": a, "sexo": SEXO_PELI.get(pe, "h"), "foto": f"assets/img/reparto/{img}.jpg"}
            for pe, a, img, _ in REPARTO if pe not in INSPIRADO]
    libro = [{"id": i, "nombre": n, "tipo": t, "sexo": sx, "desc": d,
              "foto": f"assets/img/libro/{i}.jpg" if os.path.exists(os.path.join(_BASE, "assets", "img", "libro", f"{i}.jpg")) else None}
             for i, n, t, sx, d in LIBRO_ENCUESTA]
    return json.dumps({"peli": peli, "libro": libro}, ensure_ascii=False).replace("</", "<\\/")

AVISO_ENCUESTA = ('<div class="aviso enc-aviso"><p><strong>Cómo funciona.</strong> Puedes votar una vez por cada personaje de la película. '
    'Solo guardamos la pareja que eliges y la fecha: ni tu nombre ni tu correo. El servicio que guarda los votos (Supabase) registra técnicamente la IP de la conexión, como cualquier servidor web.</p></div>'
    if SUPABASE_KEY else
    '<div class="aviso enc-aviso"><p><strong>Modo de prueba.</strong> Tus respuestas se guardan solo en este navegador y no se envían a ningún sitio. Los porcentajes solo cuentan los votos hechos aquí.</p>'
    '<p class="enc-herramientas"><button type="button" class="btn sec" id="enc-simular">Simular 50 votos</button> <button type="button" class="btn sec" id="enc-borrar">Borrar votos de prueba</button></p></div>')

PAGINAS["encuesta/"] = dict(
    titulo="Encuesta: ¿quién es quién en El Director? · Juega a emparejar",
    activo="encuesta/",
    desc="Elige un personaje de la película El Director y di qué personaje del libro de David Jiménez crees que es. Un juego de opinión, con resultados.",
    cuerpo=f"""<div class="contenedor">
{migas(("Inicio", ""), ("Encuesta", None))}
<p class="antetitulo">Encuesta · Juego de opinión</p>
<h1>¿Quién es quién?</h1>
<div class="lectura">
<p class="entradilla">La película cambia casi todos los nombres del libro. Elige un personaje de la película y dinos qué personaje del libro crees que es. <strong>Ayúdanos a descubrirlos.</strong></p>
</div>
{AVISO_ENCUESTA}
<section id="encuesta" class="encuesta" data-base="{{r}}"{f' data-supabase-url="{SUPABASE_URL}" data-supabase-key="{SUPABASE_KEY}"' if SUPABASE_KEY else ""} aria-label="Juego de emparejar personajes">
  <div class="enc-paso"><noscript><p>La encuesta necesita JavaScript.</p></noscript></div>
  <p class="enc-vivo" aria-live="polite"></p>
</section>
<script type="application/json" id="encuesta-datos">{datos_encuesta()}</script>
<h2>Resultados</h2>
<div id="encuesta-resultados" class="enc-resultados"></div>
<div class="aviso"><p><strong>Es un juego de opinión.</strong> Los resultados no confirman nada: solo muestran qué piensan quienes participan. Lo confirmado está en <a href="{{r}}personajes/">Quién es quién</a>.</p>
<p>En internet circulan varias listas que atribuyen nombres reales a los apodos del libro. No las enlazamos ni las damos por buenas: lo nuestro es solo un juego para animar a participar, a leer el libro y a ver la película. La mejor forma de conocer a cada personaje es <a href="{{r}}libro/#donde-leer">leer <i>El director</i></a> y <a href="{{r}}pelicula/#donde-ver">verla en el cine</a>.</p>
<p>Los apodos son personajes del libro: David Jiménez los usó para proteger a quienes aún trabajaban en el diario. Aquí solo se emparejan con personajes de la película; no intentamos averiguar quién es la persona real detrás de cada apodo.</p>
<p>David Jiménez y El Cardenal no están en el juego porque su relación ya está confirmada. Las fotos son de Wikimedia Commons; los créditos están en <a href="{{r}}metodologia-y-fuentes/#creditos">metodología</a>.</p></div>
{fuentes("wiki_libro", "beta")}
</div>""",
    ld=[ld_migas([("Inicio", ""), ("Encuesta", "encuesta/")])],
)

# ---------- Hero de las páginas interiores (mismo diseño que la portada) ----------
# ruta: (imagen en assets/img/cabeceras, ancho, alto, encuadre, voltear)
CABECERAS = {
    "personajes/": ("personajes.jpg", 1920, 1080, "60% 30%", False),
    "personajes/cardenal/": ("cardenal.jpg", 1920, 1108, "55% 25%", False),
    "personajes/david-jimenez/": ("david-jimenez.jpg", 1920, 1271, "70% 20%", True),
    "libro/": ("libro.jpg", 1920, 1080, "65% 30%", False),
    "pelicula/": ("pelicula.jpg", 1920, 1080, "70% 25%", False),
    "historia-real/": ("historia-real.jpg", 1920, 1080, "75% 30%", False),
    "preguntas-frecuentes/": ("preguntas.jpg", 1920, 1080, "80% 40%", False),
    "metodologia-y-fuentes/": ("metodologia.jpg", 1920, 1080, "65% 35%", False),
    "encuesta/": ("encuesta.jpg", 1920, 1080, "70% 30%", False),
}

def con_hero(ruta, cuerpo):
    """Saca migas, antetítulo, h1 y entradilla del principio de la página y los pone sobre una foto a sangre."""
    import re
    img, w, h, encuadre, voltear = CABECERAS[ruta]
    m = re.match(r'\s*(?:<div class="banda".*?</div></div>\s*)?<div class="contenedor"[^>]*>\s*(.*?<h1>.*?</h1>)\s*', cuerpo, re.S)
    cabeza, resto = m.group(1), cuerpo[m.end():]
    m2 = re.match(r'(<div class="lectura">)\s*(<p class="entradilla">.*?</p>)\s*', resto, re.S)
    entradilla = ""
    if m2:
        entradilla, resto = m2.group(2), m2.group(1) + "\n" + resto[m2.end():]
    estilo = f'object-position:{encuadre}' + (';transform:scaleX(-1)' if voltear else '')
    prioridad = ' fetchpriority="high"'
    if ruta == "libro/":
        # La cubierta repetida: 4 en escritorio, 3 en tableta y 1 en móvil (el CSS oculta las que sobran)
        fondo = ('<div class="hero-fondo hero-mosaico" aria-hidden="true">' +
                 "".join(f'<img src="{{r}}assets/img/portada/libro-el-director.jpg" alt="" width="780" height="1200" decoding="async"{prioridad if i == 0 else ""}>' for i in range(4)) +
                 '</div>')
    else:
        fondo = None
    alt = "David Jiménez en 2019" if ruta == "personajes/david-jimenez/" else ""
    # Las migas salen del hero a una franja propia entre el hero y el contenido.
    mg = re.search(r'<nav class="migas".*?</nav>', cabeza, re.S)
    franja = ""
    if mg:
        cabeza = cabeza.replace(mg.group(0), "")
        franja = f'<div class="migas-franja"><div class="contenedor">{mg.group(0)}</div></div>\n'
    return (f'<section class="hero hero-v3 hero-pagina">'
            + (fondo or f'<img class="hero-fondo" src="{{r}}assets/img/cabeceras/{img}" alt="{alt}" width="{w}" height="{h}" style="{estilo}" fetchpriority="high" decoding="async">') +
            f'<div class="contenedor hero-texto">{cabeza}{entradilla}</div></section>\n'
            f'{franja}<div class="contenedor">\n{resto}')

def main():
    docs = SALIDA
    if os.path.isdir(docs):
        shutil.rmtree(docs)
    os.makedirs(os.path.join(docs, "assets"))
    base = os.path.dirname(os.path.abspath(__file__))
    shutil.copy(os.path.join(base, "assets", "estilos.css"), os.path.join(docs, "assets", "estilos.css"))
    for js in ("video.js", "slider.js", "encuesta.js", "cookies.js"):
        shutil.copy(os.path.join(base, "assets", js), os.path.join(docs, "assets", js))
    shutil.copytree(os.path.join(base, "assets", "img"), os.path.join(docs, "assets", "img"))
    open(os.path.join(docs, "assets", "icono.svg"), "w").write(ICONO)
    open(os.path.join(docs, ".nojekyll"), "w").write("")
    open(os.path.join(docs, "CNAME"), "w").write(DOMINIO + "\n")
    for ruta, p in PAGINAS.items():
        destino = os.path.join(docs, ruta, "index.html")
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        with open(destino, "w", encoding="utf-8") as fh:
            cuerpo = con_hero(ruta, p["cuerpo"]) if ruta in CABECERAS else p["cuerpo"]
            fh.write(plantilla(ruta, p["titulo"], p["desc"], cuerpo, p.get("ld"), p.get("activo"), p.get("portada", False), ruta in CABECERAS))
    # 404 con rutas absolutas (GitHub Pages la sirve en cualquier profundidad)
    pagina404 = plantilla("", "Página no encontrada · El Director", "Página no encontrada.", NO_ENCONTRADA.format(repo=REPO))
    pagina404 = pagina404.replace('href="assets/', f'href="{RAIZ}assets/').replace('src="assets/', f'src="{RAIZ}assets/').replace('<meta name="robots" content="index, follow, max-image-preview:large">', '<meta name="robots" content="noindex">')
    for u, _ in MENU + [("metodologia-y-fuentes/", ""), ("personajes/", ""), ("libro/", ""), ("pelicula/", ""), ("historia-real/", ""), ("personajes/david-jimenez/", ""), ("preguntas-frecuentes/", ""), ("encuesta/", ""), ("metodologia-y-fuentes/#rectificaciones", ""), ("metodologia-y-fuentes/#cookies", "")]:
        pagina404 = pagina404.replace(f'href="{u}"', f'href="{RAIZ}{u}"')
    pagina404 = pagina404.replace('<a class="marca" href="">', f'<a class="marca" href="{RAIZ}">')
    open(os.path.join(docs, "404.html"), "w", encoding="utf-8").write(pagina404)
    urls = "".join(f"<url><loc>{SITE}{r}</loc><lastmod>{ACTUALIZADO}</lastmod></url>" for r in PAGINAS)
    open(os.path.join(docs, "sitemap.xml"), "w").write(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>')
    # robots.txt solo es efectivo en la raíz del dominio; se deja por si se usa dominio propio
    open(os.path.join(docs, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {SITE}sitemap.xml\n")
    print(f"{len(PAGINAS)} páginas generadas en {docs} para {SITE}")

if __name__ == "__main__":
    main()
