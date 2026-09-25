"""
Paquete web: aplicación Flask del prototipo PowerFit.

create_app() es una "fábrica de aplicaciones": arma y configura la app.
Permite crear una app distinta para las pruebas (con BD en memoria)
sin tocar la base de datos real.
"""

import os  # Para leer variables de entorno (configuración y secretos)
import secrets  # Para generar una clave secreta temporal si no se configuró una
from datetime import date, timedelta  # Para la duración de la sesión y los filtros de fecha
from flask import Flask, render_template  # Clase principal de Flask y renderizado de plantillas
import conectar  # Módulo de conexión a la BD
from dao.esquema import crear_esquema  # Crea las tablas al iniciar
from model.validaciones import formatear_rut  # Para el filtro de plantillas "rut"
from web.db import cerrar_conexion  # Cierra la conexión al terminar cada petición
from web.seguridad import token_csrf, trabajador_actual, validar_csrf  # Controles de seguridad


def create_app(config: dict | None = None) -> Flask:  # Fábrica de la aplicación
    app = Flask(__name__)  # Crea la aplicación Flask (busca templates/ y static/ en esta carpeta)

    # ---------- Configuración ----------
    app.config.update(  # Configuración por defecto
        SECRET_KEY=os.environ.get("POWERFIT_SECRET_KEY") or secrets.token_hex(32),  # Clave para firmar la cookie de sesión
        DATABASE=os.environ.get("POWERFIT_DB", conectar.RUTA_POR_DEFECTO),  # Ruta de la base de datos
        CARGAR_DEMO=os.environ.get("POWERFIT_DEMO", "1") == "1",  # Si la BD está vacía, carga datos de ejemplo
        SESSION_COOKIE_HTTPONLY=True,  # JavaScript no puede leer la cookie de sesión (mitiga robo por XSS)
        SESSION_COOKIE_SAMESITE="Lax",  # La cookie no viaja en peticiones de otros sitios (mitiga CSRF)
        SESSION_COOKIE_SECURE=os.environ.get("POWERFIT_HTTPS", "0") == "1",  # En el hosting con HTTPS: solo por conexión cifrada
        PERMANENT_SESSION_LIFETIME=timedelta(hours=2),  # La sesión expira a las 2 horas
        MAX_CONTENT_LENGTH=64 * 1024,  # Rechaza peticiones de más de 64 KB (evita abusos)
    )
    if config:  # Si se entregó configuración extra (por ejemplo, en las pruebas)...
        app.config.update(config)  # ...reemplaza los valores por defecto

    # ---------- Base de datos ----------
    _inicializar_bd(app)  # Crea las tablas (y datos demo si corresponde)
    app.teardown_appcontext(cerrar_conexion)  # Al terminar cada petición se cierra la conexión

    # ---------- Seguridad ----------
    app.before_request(validar_csrf)  # Antes de cada petición: valida el token CSRF de los POST
    app.after_request(_cabeceras_seguridad)  # Después de cada petición: agrega cabeceras de seguridad

    # ---------- Plantillas ----------
    app.context_processor(lambda: {"usuario": trabajador_actual(), "csrf_token": token_csrf})  # Variables disponibles en TODAS las plantillas
    app.add_template_filter(_formato_clp, "clp")  # Filtro {{ monto|clp }} -> $15.000
    app.add_template_filter(formatear_rut, "rut")  # Filtro {{ rut|rut }} -> 12.345.678-5
    app.add_template_filter(_formato_fecha, "fecha")  # Filtro {{ fecha|fecha }} -> 25-09-2026

    # ---------- Rutas (Blueprints) ----------
    from web.auth import bp as auth_bp  # Login y logout
    from web.panel import bp as panel_bp  # Panel principal
    from web.socios import bp as socios_bp  # Socios (recepcionista)
    from web.inscripciones import bp as inscripciones_bp  # Inscripciones y cobros (recepcionista)
    from web.clases import bp as clases_bp  # Clases (crear/editar solo instructor)
    from web.asistencia import bp as asistencia_bp  # Asistencia (instructor)
    from web.ingreso import bp as ingreso_bp  # Control de ingreso
    from web.suplementos import bp as suplementos_bp  # Venta de suplementos (recepcionista)
    for blueprint in (auth_bp, panel_bp, socios_bp, inscripciones_bp, clases_bp, asistencia_bp, ingreso_bp, suplementos_bp):  # Recorre los módulos
        app.register_blueprint(blueprint)  # Registra cada grupo de rutas en la app

    # ---------- Páginas de error ----------
    for codigo in (400, 403, 404, 500):  # Códigos de error con página propia
        app.register_error_handler(codigo, _pagina_error)  # Muestra una página amigable (sin detalles internos)

    return app  # Retorna la aplicación lista


# ---------------- Funciones auxiliares ----------------

def _inicializar_bd(app: Flask) -> None:  # Prepara la base de datos al arrancar
    conexion = conectar.crear_conexion(app.config["DATABASE"])  # Abre una conexión temporal
    try:  # Asegura que la conexión se cierre aunque haya errores
        crear_esquema(conexion)  # Crea todas las tablas si no existen
        if app.config["CARGAR_DEMO"]:  # Si está activada la carga de datos demo...
            from seed import cargar_datos_demo  # ...importa la función (solo cuando se necesita)
            cargar_datos_demo(conexion)  # ...y la ejecuta (no hace nada si ya hay datos)
    finally:  # Pase lo que pase...
        conexion.close()  # ...cierra la conexión temporal


def _cabeceras_seguridad(respuesta):  # Agrega cabeceras HTTP de seguridad a cada respuesta
    respuesta.headers["X-Content-Type-Options"] = "nosniff"  # El navegador no "adivina" tipos de archivo
    respuesta.headers["X-Frame-Options"] = "DENY"  # Nadie puede incrustar la app en un iframe (clickjacking)
    respuesta.headers["Referrer-Policy"] = "same-origin"  # No filtra URLs internas a otros sitios
    respuesta.headers["Content-Security-Policy"] = (  # Solo se cargan recursos del propio sitio
        "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; "  # Scripts SOLO desde archivos propios (estilos en línea permitidos para las barras de cupo)
        "img-src 'self' data:; frame-ancestors 'none'; form-action 'self'"  # Sin iframes externos y formularios solo hacia este sitio
    )
    return respuesta  # Retorna la respuesta modificada


def _formato_clp(monto) -> str:  # Formatea montos en pesos chilenos
    return "$" + f"{int(round(monto or 0)):,}".replace(",", ".")  # Ej: 15000 -> "$15.000"


def _formato_fecha(valor) -> str:  # Formatea fechas al estilo chileno
    if isinstance(valor, date):  # Si es un objeto fecha...
        return valor.strftime("%d-%m-%Y")  # ...lo muestra como día-mes-año
    if isinstance(valor, str) and len(valor) >= 10:  # Si es texto ISO (AAAA-MM-DD...)...
        return f"{valor[8:10]}-{valor[5:7]}-{valor[0:4]}"  # ...lo reordena a día-mes-año
    return valor or ""  # Cualquier otro caso: lo muestra tal cual


def _pagina_error(error):  # Página común para los errores HTTP
    codigo = getattr(error, "code", 500)  # Obtiene el código (500 si es un error inesperado)
    mensajes = {  # Mensajes amigables por código
        400: "La solicitud no es valida.",
        403: "No tienes permiso para realizar esta accion.",
        404: "La pagina que buscas no existe.",
        500: "Ocurrio un error inesperado. Intenta nuevamente.",
    }
    detalle = getattr(error, "description", "") if codigo == 400 else ""  # Solo en 400 se muestra el detalle (es seguro)
    return render_template("error.html", codigo=codigo, mensaje=mensajes.get(codigo, "Error"), detalle=detalle), codigo  # Nunca muestra trazas internas
