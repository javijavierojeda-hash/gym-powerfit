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

  // ---------- RUT: se escribe sin puntos y el sistema lo ordena solo ----------
  // Es solo comodidad: el servidor SIEMPRE vuelve a validar el RUT (módulo 11).
  const calcularDv = (cuerpo) => {                               // Dígito verificador con el algoritmo módulo 11
    let suma = 0, multiplicador = 2;                             // La serie parte en 2
    for (const digito of [...cuerpo].reverse()) {                // Recorre los dígitos de derecha a izquierda
      suma += Number(digito) * multiplicador;                    // Suma cada dígito por su multiplicador
      multiplicador = multiplicador < 7 ? multiplicador + 1 : 2; // Serie 2,3,4,5,6,7 que se repite
    }
    const resto = 11 - (suma % 11);                              // Fórmula del módulo 11
    return resto === 11 ? "0" : resto === 10 ? "K" : String(resto); // 11 -> 0, 10 -> K
  };
  document.querySelectorAll("input[data-rut]").forEach((campo) => { // Cada campo marcado como RUT
    const ayuda = campo.closest(".campo")?.querySelector("[data-rut-ayuda]"); // Pista de la etiqueta (si existe)
    const textoAyuda = ayuda ? ayuda.textContent : "";           // Texto original de la pista
    const mostrar = (error) => {                                 // Muestra u oculta el error
      campo.classList.toggle("mal", Boolean(error));             // Borde rojo si hay error
      if (ayuda) {                                               // La pista pasa a ser el mensaje de error
        ayuda.textContent = error || textoAyuda;                 // Error o pista original
        ayuda.classList.toggle("mal", Boolean(error));           // Rojo solo si hay error
      }
    };
    campo.addEventListener("input", () => {                      // Mientras se escribe...
      const limpio = campo.value.toUpperCase().replace(/[^0-9K-]/g, ""); // ...quita puntos, espacios y letras (salvo K)
      if (limpio !== campo.value) campo.value = limpio;          // Solo reescribe si cambió (no mueve el cursor de más)
      mostrar("");                                               // Mientras escribe no se muestra error
    });
    campo.addEventListener("blur", () => {                       // Al salir del campo...
      const sinGuion = campo.value.replace(/-/g, "");            // Quita los guiones que haya
      if (!sinGuion) { mostrar(""); return; }                    // Campo vacío: nada que revisar
      campo.value = sinGuion.length > 1 ? `${sinGuion.slice(0, -1)}-${sinGuion.slice(-1)}` : sinGuion; // Pone el guion antes del DV
      const [cuerpo, dv] = campo.value.split("-");               // Separa cuerpo y dígito verificador
      const valido = /^\d{7,8}$/.test(cuerpo || "") && calcularDv(cuerpo) === dv; // Formato y DV correctos
      mostrar(valido ? "" : "inválido: revisa el dígito verificador"); // Avisa antes de enviar
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
