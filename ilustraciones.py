#!/usr/bin/env python3
"""Ilustraciones propias en SVG (sin derechos de terceros).

Genera en assets/img/:
  papel-triturado.svg  tiras de periódico (remite a la portada del libro)
  butacas.svg          patio de butacas rojas (remite a la imagen promocional)
  silueta.svg          retrato "censurado" para personas sin foto libre
  og-fuente.svg        base de la imagen para redes (se convierte a PNG 1200x630)
"""
import os, random

DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "img")
PAPEL, TINTA, PETROLEO, ORO, BUTACA = "#ece8df", "#1d1d1b", "#0f2a2c", "#e3b23c", "#b3262d"


def papel_triturado(ancho=1200, alto=520, semilla=1971):
    rnd = random.Random(semilla)
    tiras = []
    x = -40
    while x < ancho + 40:
        w = rnd.randint(26, 46)
        rot = rnd.uniform(-7, 7)
        y0 = rnd.randint(-60, 40)
        h = alto + rnd.randint(40, 140)
        tono = rnd.choice(["#e9e4d8", "#e2dccd", "#ece8df", "#d9d2c1"])
        lineas = []
        ly = y0 + 14
        while ly < y0 + h - 10:
            if rnd.random() < 0.12:  # titular
                lineas.append(f'<rect x="{x+4}" y="{ly}" width="{w-8}" height="7" fill="{TINTA}" opacity=".8"/>')
                ly += 14
            else:
                lw = (w - 8) * rnd.uniform(.55, 1)
                lineas.append(f'<rect x="{x+4}" y="{ly}" width="{lw:.1f}" height="2.2" fill="{TINTA}" opacity=".45"/>')
                ly += 6
            if rnd.random() < 0.04:  # palabra tachada
                lineas.append(f'<rect x="{x+4}" y="{ly}" width="{(w-8)*.7:.1f}" height="5" fill="{TINTA}"/>')
                ly += 10
        tiras.append(
            f'<g transform="rotate({rot:.2f} {x+w/2} {alto/2})"><rect x="{x}" y="{y0}" width="{w}" height="{h}" fill="{tono}"/>{"".join(lineas)}</g>'
        )
        x += w - rnd.randint(2, 8)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {ancho} {alto}" preserveAspectRatio="xMidYMid slice">'
            f'<rect width="{ancho}" height="{alto}" fill="{PETROLEO}"/>{"".join(tiras)}</svg>')


def butacas(ancho=1200, alto=420):
    filas = []
    for f in range(9):
        y = 40 + f * 44
        escala = 0.62 + f * 0.06
        w, h = 34 * escala, 38 * escala
        paso = w + 8 * escala
        n = int(ancho / paso) + 2
        desp = (f % 2) * paso / 2
        luz = 0.55 + f * 0.05
        for i in range(n):
            x = -paso + i * paso + desp
            filas.append(
                f'<g opacity="{luz:.2f}"><rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{5*escala:.1f}" fill="{BUTACA}"/>'
                f'<rect x="{x:.1f}" y="{y+h*.62:.1f}" width="{w:.1f}" height="{h*.38:.1f}" rx="{4*escala:.1f}" fill="#7d1a1f"/></g>'
            )
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {ancho} {alto}" preserveAspectRatio="xMidYMid slice">'
            f'<rect width="{ancho}" height="{alto}" fill="#120d0e"/>{"".join(filas)}'
            f'<rect width="{ancho}" height="{alto}" fill="url(#v)"/><defs><linearGradient id="v" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{PETROLEO}" stop-opacity=".9"/><stop offset=".55" stop-color="{PETROLEO}" stop-opacity="0"/></linearGradient></defs></svg>')


def silueta():
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 480 600">'
            f'<rect width="480" height="600" fill="#163a3d"/>'
            f'<g fill="#1f4b4f"><circle cx="240" cy="230" r="105"/><path d="M60 600c0-120 80-205 180-205s180 85 180 205z"/></g>'
            f'<rect x="110" y="200" width="260" height="46" fill="{TINTA}"/>'
            f'<text x="240" y="560" text-anchor="middle" font-family="IBM Plex Mono,Menlo,monospace" font-size="20" letter-spacing="4" fill="#a9b6b3">SIN FOTO LIBRE</text></svg>')


def og():
    # Lienzo cuadrado 1200x1200 (qlmanage renderiza cuadrado y recorta 285 px arriba); el contenido va desplazado 285 px.
    fondo = papel_triturado(1200, 630, 2019).replace('preserveAspectRatio="xMidYMid slice"', 'x="0" y="0" width="1200" height="630"')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1200" viewBox="0 0 1200 1200">'
            f'<rect width="1200" height="1200" fill="{PETROLEO}"/><g transform="translate(0 285)">{fondo}'
            f'<rect width="1200" height="630" fill="{PETROLEO}" opacity=".82"/>'
            f'<text x="70" y="120" font-family="Menlo,monospace" font-size="24" letter-spacing="5" fill="#a9b6b3">QUIÉN ES QUIÉN · LIBRO Y PELÍCULA</text>'
            f'<text x="66" y="330" font-family="Impact,Haettenschweiler,sans-serif" font-size="190" fill="{PAPEL}">EL DIRECTOR</text>'
            f'<text x="72" y="410" font-family="Impact,sans-serif" font-size="58" letter-spacing="8" fill="{ORO}">DEL LIBRO A LA PELÍCULA</text>'
            f'<rect x="70" y="480" width="520" height="64" fill="{ORO}"/>'
            f'<text x="92" y="524" font-family="Menlo,monospace" font-size="26" letter-spacing="2" fill="{PETROLEO}">EN CINES EL 20 DE NOVIEMBRE</text></g></svg>')


if __name__ == "__main__":
    os.makedirs(DIR, exist_ok=True)
    for nombre, svg in [("papel-triturado.svg", papel_triturado()), ("butacas.svg", butacas()),
                        ("silueta.svg", silueta()), ("og-fuente.svg", og())]:
        with open(os.path.join(DIR, nombre), "w", encoding="utf-8") as fh:
            fh.write(svg)
        print(nombre, len(svg) // 1024, "KB")
