# El Director. Del libro a la película

Web informativa e independiente que relaciona a las personas reales del libro *El director* (David Jiménez, Libros del K.O., 2019) con los personajes de la película de Dani de la Orden (2026).

- Publicada en: https://pedrognrd.github.io/el-director/
- Sin publicidad, sin afiliación y sin cookies.
- Rectificaciones: abre una incidencia en este repositorio.

## Cómo se genera

El contenido está en `build.py`. Para regenerar el sitio:

```bash
python3 build.py pedrognrd el-director
```

La salida va a `docs/`, que es la carpeta que publica GitHub Pages. Los estilos viven en `assets/estilos.css`.

## Multimedia

- Fotos: Wikimedia Commons con licencia CC BY / CC BY-SA, recortadas (`assets/img/*.jpg`). Créditos en `build.py` (`FOTOS`) y en /metodologia-y-fuentes/#creditos.
- Ilustraciones propias: `python3 ilustraciones.py` regenera papel triturado, butacas, silueta y la base de la imagen para redes.
- Vídeos: YouTube en modo de privacidad mejorada; el reproductor solo se carga al pulsar (`assets/video.js`).
