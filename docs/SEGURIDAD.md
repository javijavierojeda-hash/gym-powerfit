# 🔐 Seguridad — checklist de Programación Orientada a Objeto Seguro

Cada control indica **qué amenaza evita** y **dónde está en el código**. Todos tienen pruebas en `tests/`.

| # | Amenaza | Control aplicado | Dónde |
|---|---|---|---|
| 1 | **Robo de contraseñas** si se filtra la BD | Hash PBKDF2-SHA256 con *salt* aleatorio y 260.000 iteraciones. Nunca se guarda ni se muestra la contraseña | `model/trabajador.py` → `generar_hash()` |
| 2 | **Ataque por tiempo** (*timing attack*) al comparar | `hmac.compare_digest` compara en tiempo constante | `Trabajador.login()`, `web/seguridad.py` → `validar_csrf()` |
| 3 | **Enumeración de usuarios** | Mensaje de error genérico + verificación "ficticia" que tarda lo mismo si el RUT no existe | `web/auth.py`, `verificacion_ficticia()` |
| 4 | **Fuerza bruta** en el login | 5 intentos fallidos → bloqueo de 5 minutos (HTTP 429) | `web/seguridad.py` → `registrar_fallo()` |
| 5 | **Inyección SQL** | 100% consultas parametrizadas (`?`); los nombres de tabla son constantes internas | Todos los archivos de `dao/` |
| 6 | **XSS** (inyectar scripts) | Jinja escapa todo lo impreso; CSP `script-src 'self'` bloquea scripts en línea (el JS está en `static/js/app.js`) | `web/templates/`, `web/__init__.py` |
| 7 | **CSRF** (formularios enviados desde otro sitio) | Token secreto por sesión en cada POST + cookie `SameSite=Lax`; logout solo por POST | `web/seguridad.py`, macro `csrf()` |
| 8 | **Robo de sesión** | Cookie `HttpOnly`, `Secure` con HTTPS, expira en 2 h; `session.clear()` al iniciar sesión (*session fixation*) | `web/__init__.py`, `iniciar_sesion()` |
| 9 | **Acceso no autorizado** (control de acceso roto) | `@login_requerido` y `@requiere_rol(...)` en el servidor (no solo ocultar botones). Recepcionista → 403 en clases; instructor → 403 en clases ajenas | `web/seguridad.py`, `web/clases.py` |
| 10 | **Datos manipulados desde el navegador** | Se valida TODO en el servidor: RUT, mes permitido, ids de clases existentes, días, horas, cantidades, socio inscrito en la clase | `web/*.py` y setters del modelo |
| 11 | **Datos inválidos en el dominio** | Encapsulamiento: atributos privados, setters con validación, colecciones expuestas como tuplas | `model/` |
| 12 | **Inconsistencias por operaciones concurrentes** | Transacciones `BEGIN IMMEDIATE`; cupo recontado en la BD; `UPDATE ... WHERE stock >= ?`; `WHERE pagada = 0` | `dao/dao.py`, `inscripcion_mensual_dao.py`, `suplemento_dao.py` |
| 13 | **Integridad referencial** | `PRAGMA foreign_keys = ON`, `UNIQUE`, `CHECK`, `ON DELETE CASCADE` | `conectar.py`, `crear_tabla()` de cada DAO |
| 14 | **Datos externos no confiables** (API del dólar) | Timeout 5 s, validación de tipo y rango (100–5000), respaldo si falla | `services/dolar_service.py` |
| 15 | **Clickjacking** | `X-Frame-Options: DENY` + CSP `frame-ancestors 'none'` | `web/__init__.py` |
| 16 | **Redirección abierta** (*open redirect*) | `siguiente` solo acepta rutas internas (`/algo`, no `//otro-sitio`) | `web/auth.py` |
| 17 | **Filtración de información en errores** | Páginas de error propias sin trazas; `debug` apagado por defecto | `web/__init__.py`, `app.py` |
| 18 | **Secretos en el repositorio** | `SECRET_KEY` por variable de entorno; `.env` y `*.db` en `.gitignore` | `.gitignore`, `web/__init__.py` |
| 19 | **Peticiones abusivas** | `MAX_CONTENT_LENGTH` de 64 KB; largos máximos en formularios | `web/__init__.py`, plantillas |

## Pendiente para un sistema en producción (fuera del alcance del prototipo)

- Guardar los intentos de login en la BD o Redis (hoy están en memoria y se reinician al reiniciar la app).
- Cambiar las contraseñas de demostración y permitir que cada trabajador cambie la suya desde la web (`Trabajador.cambiar_password()` ya existe).
- Registro de auditoría (quién hizo cada cobro o venta ya se guarda; faltaría un visor).
- HTTPS obligatorio (PythonAnywhere lo entrega; activar `POWERFIT_HTTPS=1`).
