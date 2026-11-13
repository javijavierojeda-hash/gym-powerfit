/* Se carga en <head> sin defer: marca el <html> antes de pintar para que
   los elementos animados partan ocultos y no "parpadeen".
   Es un archivo externo (no inline) para cumplir la Content-Security-Policy. */
(function () {
  var root = document.documentElement;
  var reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reduceMotion) return;

  root.classList.add("js-motion");
  try {
    if (!sessionStorage.getItem("cm-visited")) root.classList.add("js-preload");
    if (sessionStorage.getItem("cm-transition") === "1") root.classList.add("is-entering");
  } catch (e) { /* almacenamiento bloqueado: seguimos sin preloader ni cortina */ }

  // Red de seguridad: si main.js no alcanza a iniciar (red lenta, error),
  // se quitan las clases para que el contenido nunca quede oculto.
  setTimeout(function () {
    if (!window.__cmReady) root.classList.remove("js-motion", "js-preload", "is-entering");
  }, 5000);
})();
