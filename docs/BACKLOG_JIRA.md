# 📋 Backlog Jira — GYM POWER FIT DESARROLLO (clave `GPF`)

Backlog completo del desarrollo del prototipo PowerFit, listo para cargarse en Jira.
Cada historia incluye: descripción de usuario, criterios de aceptación (verificables),
tareas técnicas, consideraciones de seguridad, puntos, responsable y sprint.

**Equipo:** Javier Ojeda · Javier Concha
**Asignatura:** Programación Orientada a Objeto Seguro (TI3V21 · 114-2B-F1)
**Referencia de arquitectura:** repo del profesor `michaelarjelm/Taller-Mecanico` (model / dao / conectar.py / main.py)

---

## 0. Acuerdos del equipo

### Convenciones Jira ↔ GitHub
| Elemento | Formato | Ejemplo |
|---|---|---|
| Rama | `feature/GPF-<n>-<descripcion-corta>` | `feature/GPF-12-validar-rut` |
| Commit | `<Tipo>(GPF-<n>): <qué se hizo>` + cuerpo explicando el porqué | `Feat(GPF-12): validar RUT con algoritmo módulo 11` |
| Pull Request | `GPF-<n> <Título de la historia>` | `GPF-12 Socio con validación de RUT` |

Tipos de commit (mismo estilo del profesor): `Feat`, `Fix`, `Refactor`, `Docs`, `Test`, `Chore`.

### Flujo de trabajo
1. Tomar la historia en Jira → mover a **En curso**.
2. Crear rama desde `main` con la clave de la historia.
3. Desarrollar + comentar cada línea + pruebas.
4. Abrir PR → mover a **En revisión** → el compañero revisa y aprueba.
5. Merge a `main` → mover a **Finalizado** y anotar en la bitácora del README.

### ✅ Definition of Done (aplica a TODAS las historias)
- [ ] Código con **comentario en cada línea lógica** y docstring en cada clase/método (estilo del profe).
- [ ] *Type hints* en atributos y firmas; atributos privados (`__x`) con `@property` cuando corresponda.
- [ ] Consultas SQL **siempre parametrizadas** (`?`), nunca concatenando texto.
- [ ] Pruebas `pytest` de los criterios de aceptación pasando.
- [ ] PR revisado y aprobado por el compañero.
- [ ] Commit(s) con la clave `GPF-<n>` y cuerpo explicativo.
- [ ] Bitácora del `README.md` actualizada con la fecha y el avance.

### Supuestos de negocio (definidos por el equipo, ajustables)
| Tipo de clase | Cupo | Duración | Regla `cupos_disponibles()` | Precio mensual |
|---|---|---|---|---|
| **Yoga** | 20 | 60 min | `cupo_maximo − inscritos` | $15.000 |
| **Spinning** | 15 bicicletas | 45 min | `bicicletas_operativas − inscritos` (una bici en mantención reduce el cupo) | $18.000 |
| **Crossfit** | 12 | 50 min | `cupo_maximo − 2 (reservados a socios nuevos) − inscritos` | $22.000 |

- El total de la inscripción mensual = suma del precio de cada clase reservada.
- Pagar la mensualidad extiende la membresía hasta el último día del mes pagado.
- Dólar del día: API pública `https://mindicador.cl/api/dolar`, con valor de respaldo si no responde.

---

## 🏃 Sprints

| Sprint | Fechas (propuestas) | Objetivo |
|---|---|---|
| **Sprint 1 — Dominio y persistencia** | 28 sep → 11 oct 2026 | Tener todas las clases del UML implementadas en `model/`, con sus reglas de negocio y excepciones, persistiendo en SQLite con el patrón DAO, y una demo por consola. |
| **Sprint 2 — Web, calidad y entrega** | 12 oct → 25 oct 2026 | Prototipo web funcional con login por rol, probado, publicado en internet y documentado para presentar al profesor. |

## 👥 Carga por persona

| | Sprint 1 | Sprint 2 | Total |
|---|---|---|---|
| Javier Ojeda | 22 pts | 16 pts | 38 pts |
| Javier Concha | 21 pts | 19 pts | 40 pts |

---

# ÉPICAS

| # | Épica | Objetivo |
|---|---|---|
| E1 | 🏗️ Base técnica y arquitectura | Estructura del proyecto, conexión SQLite, DAO base y demo por consola siguiendo la arquitectura del profesor. |
| E2 | 🔐 Trabajadores y control de acceso | Trabajadores con contraseña segura y permisos por rol (instructor / recepcionista). |
| E3 | 🪪 Socios y membresías | Ficha de socio con RUT validado, membresía y control de ingreso. |
| E4 | 🧘 Clases y reservas | Tipos de clase con cupos propios, inscripción mensual con detalle y asistencia. |
| E5 | 💊 Suplementos | Venta en mesón con precio en CLP según el dólar del día. |
| E6 | 🚀 Calidad, despliegue y documentación | Pruebas, seguridad, hosting e informe final. |

---

# E1 · 🏗️ Base técnica y arquitectura

### GPF · Estructura del proyecto y convenciones
**Responsable:** Javier Ojeda · **Sprint:** 1 · **Puntos:** 2 · **Prioridad:** Highest · **Etiquetas:** `arquitectura`

**Historia:** Como equipo de desarrollo quiero una estructura de proyecto ordenada igual a la del profesor para trabajar en paralelo sin conflictos.

**Criterios de aceptación**
- Existen los paquetes `model/`, `dao/`, `services/`, `web/`, `tests/` y `docs/`, cada paquete Python con `__init__.py`.
- `.gitignore` excluye `__pycache__/`, `*.pyc`, `*.db`, `.env`, `.venv/`.
- `requirements.txt` con dependencias fijadas (`flask`, `pytest`, `requests`).
- `README.md` con descripción, cómo ejecutar y sección **Bitácora de Avances**.
- `CONTRIBUTING.md` con la convención de ramas, commits y Definition of Done.

**Tareas técnicas:** crear carpetas · `.gitignore` · `requirements.txt` · README · CONTRIBUTING.

---

### GPF · Conexión a SQLite y DAO base
**Responsable:** Javier Ojeda · **Sprint:** 1 · **Puntos:** 2 · **Prioridad:** Highest · **Etiquetas:** `dao`, `bd`

**Historia:** Como desarrollador quiero una conexión única a la base de datos y una clase DAO base para que todos los DAOs reutilicen conexión y cursor.

**Criterios de aceptación**
- `conectar.py` expone `crear_conexion()` que abre `powerfit.db` y ejecuta `PRAGMA foreign_keys = ON`.
- La ruta de la BD puede cambiarse con la variable de entorno `POWERFIT_DB` (las pruebas usan `:memory:`).
- `dao/dao.py` define `Dao` que recibe la conexión y guarda `self.conexion` y `self.cursor`.

**Seguridad:** la ruta de la BD no queda fija en el código; el archivo `.db` no se sube a GitHub.

---

### GPF · Datos de ejemplo y demo por consola
**Responsable:** Javier Concha · **Sprint:** 1 · **Puntos:** 3 · **Prioridad:** Medium · **Etiquetas:** `demo`

**Historia:** Como equipo quiero cargar datos de ejemplo y ejecutar una demo en consola para mostrar al profesor que el dominio funciona sin la web.

**Criterios de aceptación**
- `seed.py` crea todas las tablas y carga: 1 instructor, 1 recepcionista, 3 socios (uno con membresía vencida), 1 clase de cada tipo y 3 suplementos.
- `main.py` (estilo del profe) muestra en consola: tablas creadas, una inscripción mensual con 2 clases y su total, un intento de inscribir en clase llena capturando `CupoLlenoException` y un intento de ingreso con membresía vencida capturando `MembresiaVencidaException`.
- Ejecutar `seed.py` dos veces no duplica datos.

---

# E2 · 🔐 Trabajadores y control de acceso

### GPF · Clase abstracta Trabajador con login seguro
**Responsable:** Javier Ojeda · **Sprint:** 1 · **Puntos:** 3 · **Prioridad:** High · **Etiquetas:** `modelo`, `seguridad`

**Historia:** Como trabajador del gimnasio quiero ingresar con mi RUT y contraseña para que solo personal autorizado use el sistema.

**Criterios de aceptación**
- `Trabajador` es abstracta (`ABC`): `Trabajador(...)` lanza `TypeError`.
- Atributos privados `__rut`, `__nombre`, `__password_hash` con `@property` de solo lectura (el hash nunca se expone).
- La contraseña se guarda con `hashlib.pbkdf2_hmac('sha256', ...)` + *salt* aleatorio (`secrets.token_bytes`) y ≥ 200.000 iteraciones.
- `login(password)` retorna `True/False` comparando con `hmac.compare_digest`.
- Contraseña mínima de 8 caracteres; si no, `ValueError`.

**Seguridad:** nunca se guarda ni se imprime la contraseña en texto plano; comparación en tiempo constante evita *timing attacks*.
**Mejora sobre el repo del profe:** su `Usuario.autenticar()` compara hashes con `==` y sin *salt*.

---

### GPF · Instructor y Recepcionista con permisos por rol
**Responsable:** Javier Ojeda · **Sprint:** 1 · **Puntos:** 3 · **Prioridad:** High · **Etiquetas:** `modelo`, `seguridad`

**Historia:** Como administrador del gimnasio quiero que cada trabajador solo pueda hacer lo que su rol permite, para que la recepcionista no cree ni modifique clases.

**Criterios de aceptación**
- `Instructor(Trabajador)` implementa `dictar_clase(clase)` y `marcar_asistencia(clase, socio)`.
- `Recepcionista(Trabajador)` implementa `inscribir_socio(rut, nombre)`, `cobrar_mensualidad(inscripcion)` y `vender_suplemento(suplemento, cantidad)`.
- `Recepcionista` **no tiene** métodos para crear/modificar clases (restricción expresada en la estructura, como dice el informe UML).
- Cada clase expone `rol` (`"instructor"` / `"recepcionista"`) para el control de acceso en la web.

---

### GPF · DAOs de trabajadores (herencia tabla-por-tipo)
**Responsable:** Javier Ojeda · **Sprint:** 1 · **Puntos:** 3 · **Prioridad:** High · **Etiquetas:** `dao`, `bd`

**Historia:** Como desarrollador quiero persistir a los trabajadores respetando la herencia, igual que `VehiculoDao`/`AutoDao` del profesor.

**Criterios de aceptación**
- `TrabajadorDao.crear_tabla()` crea `trabajadores(rut PK, nombre, password_hash, salt)`.
- `InstructorDao` y `RecepcionistaDao` heredan de `TrabajadorDao`, llaman `super().crear_tabla()` y crean `instructores` / `recepcionistas` con `rut` PK + FK a `trabajadores`.
- Métodos `insertar()`, `buscar_por_rut()`, `listar()` con consultas parametrizadas.
- Al buscar por RUT se retorna el objeto del tipo correcto (`Instructor` o `Recepcionista`).

---

### GPF · Login web y menú según rol
**Responsable:** Javier Ojeda · **Sprint:** 2 · **Puntos:** 5 · **Prioridad:** High · **Etiquetas:** `web`, `seguridad`

**Historia:** Como trabajador quiero iniciar sesión en la web y ver solo las opciones de mi rol.

**Criterios de aceptación**
- App Flask con pantalla de login (RUT + contraseña) y botón cerrar sesión.
- La recepcionista ve: Socios, Inscripciones, Cobros, Suplementos, Control de ingreso.
- El instructor ve: Mis clases, Asistencia, Crear/editar clase.
- Decorador `@requiere_rol(...)`: si una recepcionista entra a `/clases/nueva` → **403 Prohibido**.
- Tras 5 intentos fallidos el RUT queda bloqueado 5 minutos.
- Mensaje de error genérico ("RUT o contraseña incorrectos"), sin revelar cuál falló.

**Seguridad:** `SECRET_KEY` desde variable de entorno; cookie de sesión `HttpOnly` y `SameSite=Lax`; protección CSRF en formularios.

---

# E3 · 🪪 Socios y membresías

### GPF · Socio con validación de RUT (módulo 11)
**Responsable:** Javier Ojeda · **Sprint:** 1 · **Puntos:** 3 · **Prioridad:** Highest · **Etiquetas:** `modelo`, `validacion`

**Historia:** Como recepcionista quiero que el sistema valide el RUT antes de crear la ficha para no registrar socios con datos erróneos.

**Criterios de aceptación**
- `Socio.validar_rut(rut)` (método estático) acepta `12.345.678-5`, `12345678-5` y `123456785`, y dígito verificador `K`/`k`.
- Calcula el dígito verificador con el algoritmo **módulo 11**.
- Rechaza: texto vacío, letras en el cuerpo, largo inválido o DV incorrecto.
- El constructor de `Socio` lanza `ValueError("RUT inválido")` si el RUT no es válido: **nunca se crea una ficha inválida**.
- El RUT se guarda normalizado (`12345678-5`).

**Casos de prueba:** `11.111.111-1` ✅ · `12.345.678-5` ✅ · `12.345.678-9` ❌ · `abc` ❌ · `""` ❌

---

### GPF · Membresía y excepción MembresiaVencidaException
**Responsable:** Javier Ojeda · **Sprint:** 1 · **Puntos:** 3 · **Prioridad:** Highest · **Etiquetas:** `modelo`, `excepciones`

**Historia:** Como gimnasio quiero saber si la membresía de un socio está vigente para no dejar entrar a quien no ha pagado.

**Criterios de aceptación**
- `Membresia` con `fecha_inicio`, `fecha_vencimiento`, `estado`; `esta_vigente()` = hoy ≤ vencimiento; `dias_restantes()` ≥ 0.
- `Socio` **se compone** de una `Membresia` (se crea dentro del socio, relación 1–1).
- `MembresiaVencidaException(Exception)` guarda `socio` y `fecha_vencimiento`, y su `__str__` muestra un mensaje claro.
- `Socio.puede_ingresar()` retorna `True` si está vigente y **lanza** `MembresiaVencidaException` si no.

---

### GPF · DAOs de socios y membresías
**Responsable:** Javier Ojeda · **Sprint:** 1 · **Puntos:** 3 · **Prioridad:** High · **Etiquetas:** `dao`, `bd`

**Criterios de aceptación**
- `socios(rut PK, nombre)`.
- `membresias(id PK, socio_rut UNIQUE FK → socios ON DELETE CASCADE, fecha_inicio, fecha_vencimiento, estado)` → `UNIQUE` asegura el 1–1 y `CASCADE` implementa la composición.
- `SocioDao.insertar(socio)` guarda socio + membresía en **una sola transacción**.
- `buscar_por_rut()` reconstruye el objeto `Socio` con su `Membresia`.

---

### GPF · Control de ingreso al gimnasio (web)
**Responsable:** Javier Ojeda · **Sprint:** 2 · **Puntos:** 3 · **Prioridad:** High · **Etiquetas:** `web`

**Historia:** Como recepcionista quiero ingresar el RUT de un socio en la entrada y saber al instante si puede pasar.

**Criterios de aceptación**
- Pantalla con un campo RUT y resultado grande: 🟢 **Puede ingresar** (con días restantes) o 🔴 **Membresía vencida** (con fecha de vencimiento).
- RUT inválido o inexistente → mensaje claro, sin error del servidor.
- Usa `Socio.puede_ingresar()` y captura `MembresiaVencidaException`.

---

### GPF · Inscribir socio y cobrar mensualidad (web)
**Responsable:** Javier Ojeda · **Sprint:** 2 · **Puntos:** 5 · **Prioridad:** High · **Etiquetas:** `web`

**Historia:** Como recepcionista quiero registrar socios nuevos y cobrar su mensualidad desde la web.

**Criterios de aceptación**
- Formulario de nuevo socio (RUT + nombre) que valida el RUT y avisa si ya existe.
- Listado de socios con buscador y estado de membresía (vigente / vencida).
- Cobrar mensualidad: muestra el total de la inscripción del mes, registra el pago y extiende la membresía.
- Los datos que escribe el usuario se muestran escapados (Jinja) → sin XSS.

---

# E4 · 🧘 Clases y reservas

### GPF · Clase abstracta y tipos Yoga, Spinning y Crossfit
**Responsable:** Javier Concha · **Sprint:** 1 · **Puntos:** 5 · **Prioridad:** Highest · **Etiquetas:** `modelo`, `polimorfismo`

**Historia:** Como gimnasio quiero que cada tipo de clase calcule sus cupos con su propia regla, porque cada una tiene distinto cupo y duración.

**Criterios de aceptación**
- `Clase(ABC)` con `id`, `horario`, `duracion_min`, `cupo_maximo`, `inscritos`, `instructor`, `precio_mensual`.
- `cupos_disponibles()` es **abstracto**; `esta_llena()` = `cupos_disponibles() <= 0`.
- `Yoga`, `Spinning` y `Crossfit` definen su cupo, duración y precio como constantes y **sobrescriben** `cupos_disponibles()` según la tabla de supuestos.
- `inscritos` nunca puede ser negativo ni superar el cupo (validado en el `setter`).

**Polimorfismo demostrado:** recorrer una lista de clases mixtas y llamar `cupos_disponibles()` da un resultado distinto según el tipo.

---

### GPF · Inscripción mensual con detalle y CupoLlenoException
**Responsable:** Javier Concha · **Sprint:** 1 · **Puntos:** 5 · **Prioridad:** Highest · **Etiquetas:** `modelo`, `excepciones`

**Historia:** Como recepcionista quiero reservar varias clases de un socio bajo una sola inscripción mensual, sin pasar el cupo de ninguna clase.

**Criterios de aceptación**
- `InscripcionMensual` con `id`, `mes` (`AAAA-MM`), `fecha`, `socio` y lista privada de `DetalleClaseReservada`.
- `agregar_clase(detalle)`: si la clase está llena **lanza** `CupoLlenoException` y **no** agrega el detalle; si no, lo agrega e incrementa `inscritos`.
- No se puede reservar dos veces la misma clase en la misma inscripción.
- `calcular_total()` = suma de `precio_mensual` de cada clase reservada.
- `DetalleClaseReservada.resumen()` → `"Yoga · lunes 09:00"`.
- `CupoLlenoException(Exception)` guarda la `clase` y su `__str__` indica cuál está llena.

---

### GPF · DAOs de clases, inscripciones y detalle
**Responsable:** Javier Concha · **Sprint:** 1 · **Puntos:** 5 · **Prioridad:** High · **Etiquetas:** `dao`, `bd`

**Criterios de aceptación**
- `clases(id PK, horario, duracion_min, cupo_maximo, precio_mensual, instructor_rut FK → instructores)` y tablas hijas `yoga`, `spinning`, `crossfit` (id PK + FK), igual que `autos` del profe.
- `inscripciones_mensuales(id PK, socio_rut FK, mes, fecha, UNIQUE(socio_rut, mes))`.
- `detalles_clase_reservada(id PK, inscripcion_id FK ON DELETE CASCADE, clase_id FK, dia, hora, UNIQUE(inscripcion_id, clase_id))`.
- Guardar una inscripción revisa el cupo **contando en la BD** y guarda todo en **una transacción** (si una clase está llena se hace `rollback` de toda la inscripción).

---

### GPF · Pantallas de clases e inscripción mensual (web)
**Responsable:** Javier Concha · **Sprint:** 2 · **Puntos:** 5 · **Prioridad:** High · **Etiquetas:** `web`

**Historia:** Como recepcionista quiero armar la inscripción mensual de un socio eligiendo clases con cupo, y como instructor quiero crear y editar clases.

**Criterios de aceptación**
- Listado de clases con tipo, horario, instructor y **barra de cupos** (verde / amarilla / roja).
- Formulario de inscripción: buscar socio por RUT, marcar clases, ver total en vivo, confirmar.
- Si una clase se llena, mensaje "La clase X ya alcanzó su cupo máximo" y la inscripción no se guarda.
- Crear/editar clase solo visible y permitido para el **instructor**.

---

### GPF · Instructor: mis clases y marcar asistencia
**Responsable:** Javier Concha · **Sprint:** 2 · **Puntos:** 3 · **Prioridad:** Medium · **Etiquetas:** `web`, `modelo`

**Historia:** Como instructor quiero ver mis clases y marcar la asistencia de los socios inscritos.

**Criterios de aceptación**
- Nueva tabla `asistencias(id, clase_id FK, socio_rut FK, fecha, instructor_rut FK, UNIQUE(clase_id, socio_rut, fecha))`.
- El instructor ve solo **sus** clases y la lista de socios inscritos con un check de asistencia.
- Solo se puede marcar asistencia a socios inscritos en esa clase.
- `Instructor.marcar_asistencia()` usa esta lógica.

---

# E5 · 💊 Suplementos

### GPF · Suplemento con precio según el dólar
**Responsable:** Javier Concha · **Sprint:** 1 · **Puntos:** 3 · **Prioridad:** Medium · **Etiquetas:** `modelo`, `dao`

**Historia:** Como gimnasio quiero registrar los suplementos importados con su precio en dólares para calcular su precio en pesos.

**Criterios de aceptación**
- `Suplemento` con `codigo`, `nombre`, `stock`, `precio_usd`, `precio_clp`.
- `actualizar_precio(valor_dolar)` → `precio_clp = round(precio_usd * valor_dolar)`; valor del dólar ≤ 0 → `ValueError`.
- `stock` y `precio_usd` no pueden ser negativos.
- `SuplementoDao` con `crear_tabla`, `insertar`, `listar`, `actualizar_stock`.

---

### GPF · Dólar del día (API) y venta en mesón
**Responsable:** Javier Concha · **Sprint:** 2 · **Puntos:** 3 · **Prioridad:** Medium · **Etiquetas:** `servicio`, `web`, `api`

**Historia:** Como recepcionista quiero vender suplementos con el precio en pesos del día sin calcularlo a mano.

**Criterios de aceptación**
- `services/dolar_service.py` consulta `https://mindicador.cl/api/dolar` con *timeout* de 5 s.
- Si la API falla, usa el último valor guardado y la pantalla avisa "valor de respaldo".
- El valor se cachea 1 hora (no se consulta la API en cada venta).
- Vender: elegir suplemento y cantidad → muestra total en CLP → descuenta stock; sin stock suficiente → error claro.

**Seguridad:** se valida que la respuesta de la API sea numérica y positiva antes de usarla.

---

# E6 · 🚀 Calidad, despliegue y documentación

### GPF · Pruebas automáticas con pytest
**Responsable:** Javier Concha · **Sprint:** 2 · **Puntos:** 3 · **Prioridad:** High · **Etiquetas:** `pruebas`

**Criterios de aceptación**
- Pruebas para: RUT válido/ inválido, cupos por tipo de clase, `CupoLlenoException`, `MembresiaVencidaException`, login correcto/incorrecto, precio del suplemento, 403 de recepcionista en crear clase.
- Las pruebas usan BD en memoria (no tocan `powerfit.db`).
- `pytest` pasa completo; se deja el comando en el README.

---

### GPF · Revisión de seguridad (POO Seguro)
**Responsable:** Javier Concha · **Sprint:** 2 · **Puntos:** 2 · **Prioridad:** Medium · **Etiquetas:** `seguridad`

**Criterios de aceptación**
- Checklist documentado en `docs/SEGURIDAD.md`: inyección SQL, XSS, CSRF, contraseñas, sesiones, control de acceso, secretos, validación de entradas, manejo de errores (sin mostrar trazas al usuario).
- Cada punto indica **dónde** se resolvió en el código.

---

### GPF · Publicar el prototipo en internet
**Responsable:** Javier Ojeda · **Sprint:** 2 · **Puntos:** 3 · **Prioridad:** Medium · **Etiquetas:** `despliegue`

**Criterios de aceptación**
- App corriendo en local con `flask run` (`http://localhost:5000`).
- App publicada en **PythonAnywhere** con URL pública y datos de ejemplo.
- `DEBUG` desactivado y `SECRET_KEY` configurada como variable de entorno en el hosting.
- Instrucciones de despliegue en el README.

---

### GPF · Informe final y UML actualizado
**Responsable:** Javier Concha · **Sprint:** 2 · **Puntos:** 3 · **Prioridad:** Medium · **Etiquetas:** `documentacion`

**Criterios de aceptación**
- Diagrama `.drawio` actualizado con lo agregado (precio e instructor en `Clase`, `Asistencia`).
- Informe PDF/Word: qué hace el sistema, arquitectura (capas y BD), modelo de datos, cómo ejecutarlo, capturas de pantalla, decisiones de seguridad.
- Guía de demo de 5 minutos para presentar al profesor.
