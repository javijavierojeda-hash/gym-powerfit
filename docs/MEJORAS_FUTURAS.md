# 🚀 Propuestas de mejora a futuro

Este documento reúne ideas que **no se implementan en esta versión** porque están fuera del alcance de la pauta y del enunciado del caso. El enunciado define solo dos roles (instructor y recepcionista), y el acta de la Reunión 1 dejó escrito que *"los socios no usan el sistema directamente"*.

Las dejamos documentadas como **oportunidades de mejora** para una siguiente iteración. Así queda claro qué haríamos, por qué y cómo, sin agrandar el alcance comprometido. En Scrum, cada una entraría al Product Backlog como una **solicitud de cambio del cliente**, se estimaría y se priorizaría para un sprint futuro.

| # | Mejora | Estado | Tamaño estimado |
|---|---|---|---|
| 0 | Escribir el RUT sin puntos y ordenarlo automáticamente | ✅ **Implementada** (ver al final) | Muy chica |
| 1 | Portal del socio: ver su membresía y sus clases | 💡 Propuesta | Mediana |
| 2 | El socio reserva y cancela sus propias clases | 💡 Propuesta | Mediana |
| 3 | Lista de espera cuando una clase está llena | 💡 Propuesta | Mediana-grande |

---

## 1. Portal del socio

### Problema
Hoy todo pasa por el mesón. Si un socio quiere saber hasta cuándo le dura la membresía, o en qué clases está inscrito, tiene que ir a preguntarle a la recepcionista. En horas punta eso genera fila y carga de trabajo.

### Propuesta
Un tercer rol, **Socio**, que inicia sesión con su RUT y su contraseña y ve **solo su propia información**.

| El socio puede | El socio no puede |
|---|---|
| Ver el estado de su membresía (vigente, vencida o pendiente) y su fecha de vencimiento | Ver datos de otros socios (privacidad, Ley 19.628) |
| Ver sus clases del mes y el total a pagar | Crear ni editar clases |
| Ver su historial de pagos | Cobrar, vender ni registrar socios |

### Historias de usuario
- **HU-S1** Como socio, quiero ver el estado de mi membresía para saber si puedo entrar al gimnasio.
  - *Criterio de aceptación:* muestra el estado y la fecha de vencimiento correctos según los datos de la base.
- **HU-S2** Como socio, quiero ver mis clases del mes para organizar mi semana.
  - *Criterio de aceptación:* solo aparecen las clases de su inscripción mensual, con día, hora y precio.

### Decisiones de diseño
1. **Cómo obtiene su cuenta el socio:** la recepcionista aprieta "Habilitar acceso" en la ficha del socio y el sistema envía al correo del socio un **enlace de activación** de un solo uso (vence en 24 h), donde él crea su contraseña.
   - **Por qué no un autorregistro con el RUT:** en Chile los RUT son públicos, así que no prueban identidad. Cualquiera podría crear la cuenta de otra persona.
   - **Requisito:** la ficha del socio tendría que guardar su correo, cosa que hoy no hace.
2. **Seguridad:**
   - El RUT del socio se toma **siempre de la sesión iniciada, nunca de la URL ni del formulario**. Si una ruta fuera `/socio/12345678-5`, bastaría con cambiar el número para ver los datos de otra persona. Ese error se llama IDOR y es de los más comunes.
   - El socio tiene su propio `@requiere_rol("socio")`. Si intenta abrir `/socios`, `/inscripciones` o `/clases/nueva`, recibe **403**, igual que hoy la recepcionista en `/clases/nueva`.
   - Se reutiliza lo que ya existe: contraseña con PBKDF2 y salt, bloqueo tras 5 intentos, CSRF y cookies seguras.

### Cambios técnicos
- **Modelo:** clase `Socio` con `password_hash` y `correo`. Por eso evaluaríamos que `Socio` y `Trabajador` hereden de una clase común `Usuario` (con RUT, nombre y login): así se evita duplicar la lógica de autenticación.
- **Base de datos:** columnas `correo`, `password_hash` y `acceso_habilitado` en `socios`, y una tabla `tokens_activacion`.
- **Web:** un blueprint nuevo `portal` con las vistas `/mi-cuenta` y `/mis-clases`.

---

## 2. El socio reserva y cancela sus clases

### Problema
Para cambiar o agregar una clase, el socio depende de que la recepcionista esté disponible.

### Propuesta
Desde su portal, el socio ve las clases **con cupo disponible** y se inscribe solo. También puede cancelar una reserva.

### Historias de usuario
- **HU-S3** Como socio, quiero reservar una clase con cupo para no depender del mesón.
  - *Criterio de aceptación:* la clase se agrega a su inscripción del mes y el cupo se descuenta en la misma transacción.
  - *Criterio de aceptación:* si la clase está llena, el sistema lo informa (reutiliza `CupoLlenoException`).
- **HU-S4** Como socio, quiero cancelar una reserva para liberar el cupo si no puedo asistir.
  - *Criterio de aceptación:* solo se permite hasta 2 horas antes de la clase.

### Reglas de negocio (por confirmar con el cliente)
| Pregunta | Propuesta |
|---|---|
| ¿Cómo se paga la clase que agrega el socio? | Queda **pendiente de pago** y se paga en el mesón. La regla actual (no entra quien tiene un pago pendiente) sigue funcionando sin cambios. |
| ¿Hasta cuándo se puede cancelar? | Hasta **2 horas antes** de la clase. |
| ¿Se devuelve el dinero al cancelar? | **Decisión del cliente.** Proponemos que no se devuelva en el mes en curso. |
| ¿Puede reservar con la membresía vencida? | No. Primero debe regularizar su pago. |

---

## 3. Lista de espera con oferta de cupo

### Problema
Cuando una clase está llena (por ejemplo, el Crossfit del viernes), el sistema solo dice "no hay cupos". Si después alguien cancela, el cupo queda vacío porque nadie se entera de que se liberó.

### Propuesta
Cuando la clase está llena, el sistema ofrece **"¿Quieres unirte a la lista de espera?"**. Si se libera un cupo, se le **ofrece al primero de la lista**.

```
Clase llena ──► El socio se une a la lista de espera (orden de llegada)
                         │
Alguien cancela ──► Se libera un cupo ──► Se le ofrece al 1.º de la lista
                                              │
                         ┌────────────────────┴────────────────────┐
                    Acepta dentro del plazo                  No responde a tiempo
                         │                                         │
               Queda inscrito (pendiente de pago)      La oferta pasa al siguiente
```

### Dos formas de hacerlo
| Opción | Cómo funciona | Evaluación |
|---|---|---|
| A. Automática | El primero de la lista queda inscrito de inmediato | Es simple, pero puede inscribir y cobrar a alguien que ya no quería la clase |
| **B. Oferta con plazo** ⭐ | Se le **reserva el cupo por 12 horas** para que confirme; si no confirma, pasa al siguiente | Es más justa y no se pierden cupos. **Es la que recomendamos** |

### Detalles técnicos a cuidar
- **Que nunca se venda el mismo cupo dos veces.** Liberar un cupo y ofrecérselo al siguiente debe ocurrir en **una sola transacción** (`BEGIN IMMEDIATE`), el mismo patrón que hoy usa la inscripción para no sobrevender.
- **No solo las cancelaciones abren cupos.** En Spinning, si reparan una bicicleta, sube `bicicletas_operativas` y también se libera un cupo. La lista debe avanzar en ese caso. Lo mismo pasa si se anula una inscripción impaga.
- **Los 2 cupos reservados de Crossfit** (para clases de prueba) no pasan a la lista de espera.
- **Ofertas vencidas sin un programa corriendo aparte.** Cada vez que alguien abre la clase o la lista, el sistema revisa si alguna oferta venció y la pasa al siguiente. Esto se llama "evaluación perezosa" y funciona incluso en un hosting gratuito como PythonAnywhere.
- **Avisos:**
  - Primera etapa: notificación dentro del portal ("🔔 Tienes un cupo disponible hasta las 21:00").
  - Segunda etapa: correo electrónico.
- **Límites para evitar abusos:** un socio no puede estar en la lista de una clase en la que ya está inscrito, y puede estar en un máximo de 3 listas a la vez.

### Datos
Tabla nueva `lista_espera`:

| Columna | Descripción |
|---|---|
| `id` | Identificador |
| `clase_id` | Clase |
| `mes` | Mes de la inscripción |
| `socio_rut` | Socio que espera |
| `solicitado_en` | Fecha y hora de solicitud (define el orden) |
| `estado` | `esperando` / `ofertado` / `aceptado` / `expirado` / `cancelado` |
| `oferta_vence` | Fecha y hora límite para aceptar |

Con la restricción `UNIQUE (clase_id, mes, socio_rut)` para que nadie se anote dos veces.

### Historias de usuario
- **HU-S5** Como socio, quiero unirme a la lista de espera de una clase llena para tener la opción de entrar si alguien se baja.
- **HU-S6** Como socio en lista de espera, quiero que se me avise y se me reserve el cupo por un tiempo para alcanzar a confirmarlo.

---

## Impacto en el diagrama de casos de uso
- El **Socio** pasaría de actor secundario a **actor principal**.
- **Casos de uso nuevos:**
  - Ver mi membresía.
  - Ver mis clases.
  - Reservar clase.
  - Cancelar reserva.
  - Unirse a lista de espera: «extend» de *Reservar clase*, con la condición "cupo lleno".
  - Aceptar cupo ofrecido.
- **Reutilización:** *Reservar clase* haría «include» de *Verificar cupo disponible* (CU-09), igual que la inscripción en el mesón.

## Priorización sugerida
1. **Portal de consulta (HU-S1 y HU-S2):** solo lectura, bajo riesgo, y da valor de inmediato.
2. **Reserva y cancelación (HU-S3 y HU-S4):** requiere las decisiones de negocio de la sección 2.
3. **Lista de espera (HU-S5 y HU-S6):** depende de que exista la cancelación, porque es lo que libera cupos.

---

## ✅ Mejora 0 (implementada): RUT sin puntos

- **Problema:** los campos mostraban el ejemplo `12.345.678-5`. Los usuarios creían que debían escribir los puntos, lo que es lento y propenso a errores.
- **Qué se hizo:**
  - El ejemplo ahora es `12345678-5`, con la pista "sin puntos" junto a la etiqueta. Aplica al login, al registro de socio, a la inscripción y al control de ingreso.
  - Mientras se escribe, el campo **elimina solo los puntos y los espacios**.
  - Al salir del campo, **agrega el guion** si falta (`123456785` → `12345678-5`) y **avisa si el dígito verificador no corresponde**, antes de enviar el formulario.
- **Seguridad:** es solo una ayuda visual en el navegador (`web/static/js/app.js`). El servidor **sigue validando siempre** el RUT con el algoritmo módulo 11 (`model/validaciones.py`). El servidor ya aceptaba los tres formatos: `12.345.678-5`, `12345678-5` y `123456785`.
- **Pruebas:** se agregaron 3 pruebas automáticas en `tests/test_web.py`:
  - login sin puntos y sin guion;
  - registro de socio y control de ingreso sin puntos;
  - la pista sin puntos en el formulario.
