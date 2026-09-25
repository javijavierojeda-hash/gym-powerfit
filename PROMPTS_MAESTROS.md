# 📘 Guía Maestra de Prompts: Proyecto PowerFit

Secuencia de prompts detallados para **recrear o extender** este proyecto con cualquier asistente de IA
(siguiendo el mismo formato del `PROMPTS_MAESTROS.md` del repo del profesor).

**Cómo usarla para ahorrar créditos:** un modelo potente planifica y revisa, y un modelo más económico
ejecuta cada prompt. Al terminar cada fase: ejecutar `python -m pytest`, revisar el diff y hacer commit
con el formato `Tipo(GPF-n): descripción` + cuerpo explicativo.

**Reglas que van en TODOS los prompts** (cópialas al inicio):
> "Proyecto Python 3.10+ PowerFit. Sigue la arquitectura model/ dao/ services/ web/ tests/ del repo. Comenta CADA línea lógica explicando qué hace, con docstring en cada clase y método. Usa type hints, atributos privados con @property y setters que validen. Todo SQL debe ser parametrizado con '?'. No cambies archivos que no se mencionan. Al terminar, ejecuta python -m pytest y corrige si algo falla."

---

## 🏗️ FASE 1: Modelo de dominio

**Prompt 1 — Validación de RUT**
> "Crea `model/validaciones.py` con: `limpiar_rut(rut)` que normaliza a `12345678-5` (sin puntos, K mayúscula, inserta el guion si falta); `calcular_dv(cuerpo)` con el algoritmo módulo 11 (serie 2..7, resto 11→'0', 10→'K'); `es_rut_valido(rut)` que valida el patrón `^\d{7,8}-[\dK]$` y el DV; `formatear_rut(rut)` que retorna `12.345.678-5`."

**Prompt 2 — Excepciones propias**
> "Crea `model/cupo_lleno_exception.py` (`CupoLlenoException(Exception)`, recibe la clase, mensaje 'La clase ya alcanzo su cupo maximo') y `model/membresia_vencida_exception.py` (`MembresiaVencidaException(Exception)`, recibe el socio y guarda su fecha de vencimiento). Ambas con `__str__` descriptivo."

**Prompt 3 — Membresía y Socio (composición)**
> "Crea `Membresia(fecha_inicio, fecha_vencimiento)` con `esta_vigente(hoy=None)`, `dias_restantes(hoy=None)`, `renovar_hasta(fecha)` y la propiedad `estado`. Crea `Socio(rut, nombre, fecha_inicio=None, fecha_vencimiento=None)`: valida el RUT con `validar_rut()` estático ANTES de crear la ficha (ValueError), y crea su propia Membresia (si no hay fechas queda vencida = pendiente de pago). `puede_ingresar()` lanza MembresiaVencidaException si no está vigente."

**Prompt 4 — Clases (herencia + polimorfismo)**
> "Crea `Clase(ABC)` con dia (lunes..domingo), hora (time), instructor_rut, id, inscritos (setter >= 0), constantes NOMBRE, CUPO_MAXIMO, DURACION_MIN, PRECIO_MENSUAL, `cupos_disponibles()` ABSTRACTO, `esta_llena()` y `registrar_inscrito()` que lanza CupoLlenoException. Subclases: `Yoga` (20, 60 min, 15000, cupo−inscritos), `Spinning` (15, 45 min, 18000, agrega bicicletas_operativas 0..15, bicicletas−inscritos), `Crossfit` (12, 50 min, 22000, CUPOS_RESERVADOS=2, cupo−2−inscritos)."

**Prompt 5 — Inscripción mensual**
> "Crea `DetalleClaseReservada(clase, dia=None, hora=None)` con `resumen()` y `subtotal`. Crea `InscripcionMensual(socio, mes 'AAAA-MM', fecha, id, pagada)` con lista privada de detalles expuesta como tupla, `agregar_clase(detalle)` (rechaza duplicados y pagadas; llama `registrar_inscrito()` que puede lanzar CupoLlenoException), `cargar_detalle()` para el DAO, `calcular_total()` y `marcar_pagada()` (exige al menos 1 detalle)."

**Prompt 6 — Trabajadores con login seguro**
> "Crea `Trabajador(ABC)` con rut validado, nombre y password_hash privado sin getter. `generar_hash(password)` estático: PBKDF2-SHA256, salt con `secrets.token_hex(16)`, 260000 iteraciones, formato `pbkdf2_sha256$iter$salt$hash`, mínimo 8 caracteres. `login(password)` con `hmac.compare_digest`. Propiedad abstracta `rol`. `Instructor`: `crear_clase(tipo, dia, hora)`, `dictar_clase(c)`, `marcar_asistencia(c, s)` (PermissionError si la clase no es suya; valida membresía). `Recepcionista`: `inscribir_socio`, `cobrar_mensualidad(i)` (marca pagada y renueva la membresía hasta fin de mes; rechaza doble cobro y meses terminados) y `vender_suplemento(s, cant)`. La recepcionista NO debe tener métodos para crear clases."

**Prompt 7 — Suplemento**
> "Crea `Suplemento(codigo, nombre, stock, precio_usd, precio_clp=0)` con validaciones, `actualizar_precio(valor_dolar)` (redondea a pesos, rechaza dólar <= 0) y `vender(cantidad)` que valida precio y stock y retorna el total."

## 🗄️ FASE 2: Persistencia (SQLite + DAO)

**Prompt 8 — Conexión y DAO base**
> "Crea `conectar.py` con `crear_conexion(ruta=None)` (parámetro > variable POWERFIT_DB > powerfit.db), `row_factory = sqlite3.Row` y `PRAGMA foreign_keys = ON`. Crea `dao/dao.py` con `Dao(conexion)` que guarda conexión y cursor, y un contextmanager `transaccion()` que ejecuta BEGIN IMMEDIATE / commit / rollback y se une a una transacción ya abierta."

**Prompt 9 — Herencia tabla por tipo**
> "Crea `TrabajadorDao` (tabla trabajadores) e hijos `InstructorDao`/`RecepcionistaDao` que llaman `super().crear_tabla()` y crean su tabla con rut PK + FK ON DELETE CASCADE, con insertar (transacción), buscar_por_rut (JOIN a su tabla) y listar. Igual para `ClaseDao` (tabla clases con instructor_rut FK) e hijos `YogaDao`, `SpinningDao` (con bicicletas_operativas CHECK 0..15) y `CrossfitDao`. `ClaseDao` reconstruye el tipo correcto con LEFT JOIN y CUENTA los inscritos del mes desde las reservas."

**Prompt 10 — Socios, inscripciones y resto**
> "Crea `SocioDao` + `MembresiaDao` (socio_rut UNIQUE, CASCADE; insertar ambos en una transacción), `InscripcionMensualDao` (UNIQUE socio+mes; `guardar()` recuenta el cupo en la BD dentro de la transacción y lanza CupoLlenoException con rollback; `registrar_pago()` con WHERE pagada = 0), `DetalleClaseReservadaDao` (CASCADE a la inscripción, sin cascada a la clase), `AsistenciaDao`, `SuplementoDao` (venta con `UPDATE ... WHERE stock >= ?` + historial) e `IndicadorDao`. Crea `dao/esquema.py` con `crear_esquema(conexion)` en orden de llaves foráneas."

## 🌐 FASE 3: Servicios, demo y web

**Prompt 11 — Dólar del día**
> "Crea `services/dolar_service.py`: consulta https://mindicador.cl/api/dolar con urllib y timeout 5 s, valida que `serie[0].valor` sea número entre 100 y 5000, caché de 1 hora, guarda el último valor en `indicadores` y usa ese respaldo (o 950) si la API falla. Permite inyectar la función que obtiene el JSON para las pruebas."

**Prompt 12 — Seed y main**
> "Crea `seed.py` idempotente con datos demo (2 instructores, 1 recepcionista, 6 clases, 12 socios con 2 vencidos, inscripciones del mes con un Crossfit lleno, 8 pagos, 4 suplementos) y `main.py` que crea las tablas, las lista y demuestra por consola los 6 requerimientos."

**Prompt 13 — Web Flask**
> "Crea `web/` con `create_app()`, conexión por petición, blueprints (auth, panel, socios, inscripciones, clases, asistencia, ingreso, suplementos), decoradores `@login_requerido` y `@requiere_rol`, CSRF en todos los POST, bloqueo tras 5 intentos, cabeceras de seguridad (CSP sin scripts en línea) y plantillas Jinja con tema oscuro. La recepcionista recibe 403 al crear/editar clases."

## ✅ FASE 4: Calidad

**Prompt 14 — Pruebas**
> "Crea pruebas pytest para cada requerimiento, la capa DAO con BD en memoria y la web con el cliente de pruebas de Flask (login, 403 por rol, CSRF, XSS escapado, cupo lleno, cobro, ingreso y venta). Simula la API del dólar caída con monkeypatch."
