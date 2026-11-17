// Vídeos de YouTube en modo de privacidad mejorada: el reproductor (y sus cookies)
// solo se carga cuando la persona pulsa "reproducir".
document.addEventListener("click", function (e) {
  var boton = e.target.closest("[data-video]");
  if (!boton) return;
  e.preventDefault();
  var id = boton.getAttribute("data-video");
  var iframe = document.createElement("iframe");
  iframe.src = "https://www.youtube-nocookie.com/embed/" + id + "?autoplay=1&rel=0";
  iframe.title = boton.getAttribute("data-titulo") || "Vídeo de YouTube";
  iframe.allow = "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture";
  iframe.allowFullscreen = true;
  iframe.loading = "lazy";
  boton.replaceWith(iframe);
});
