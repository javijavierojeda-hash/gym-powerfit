// =====================================================================
// PowerFit · Script del navegador
// Está en un archivo aparte (no dentro del HTML) porque la política de
// seguridad (CSP) prohíbe scripts incrustados: así un XSS no puede ejecutarse.
// =====================================================================

document.addEventListener("DOMContentLoaded", () => {           // Espera a que la página termine de cargar
  // ---------- Total en vivo de la inscripción mensual ----------
  const formulario = document.querySelector("[data-inscripcion]"); // Busca el formulario de inscripción (si existe en la página)
  if (formulario) {                                              // Solo si estamos en esa página
    const salida = formulario.querySelector("[data-total]");     // Elemento donde se muestra el total
    const formato = new Intl.NumberFormat("es-CL");              // Formateador de números chileno (15.000)
    const recalcular = () => {                                   // Función que suma los precios marcados
      let total = 0;                                             // Acumulador
      formulario.querySelectorAll("input[name=clases]:checked")  // Recorre los checkbox marcados
        .forEach((casilla) => { total += Number(casilla.dataset.precio || 0); }); // Suma el precio de cada clase
      salida.textContent = "$" + formato.format(total);          // Muestra el total formateado
    };
    formulario.addEventListener("change", recalcular);           // Recalcula cada vez que se marca/desmarca una clase
    recalcular();                                                // Calcula el total inicial
  }

  // ---------- Confirmación antes de acciones delicadas ----------
  document.querySelectorAll("form[data-confirmar]").forEach((f) => {   // Formularios que piden confirmación
    f.addEventListener("submit", (evento) => {                        // Al enviarlos...
      if (!window.confirm(f.dataset.confirmar)) evento.preventDefault(); // ...si el usuario cancela, no se envían
    });
  });

  // ---------- Muestra el campo de bicicletas solo para Spinning ----------
  const tipo = document.querySelector("select[name=tipo]");      // Selector del tipo de clase (formulario de clases)
  const bicis = document.querySelector("[data-bicicletas]");     // Campo de bicicletas operativas
  if (tipo && bicis) {                                           // Solo si ambos existen
    const actualizar = () => { bicis.hidden = tipo.value !== "spinning"; }; // Oculta el campo si no es Spinning
    tipo.addEventListener("change", actualizar);                 // Actualiza al cambiar el tipo
    actualizar();                                                // Estado inicial
  }
});
