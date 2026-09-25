"""
Seguridad de la aplicación web (asignatura: Programación Orientada a Objeto SEGURO).

Aquí se concentran los controles de seguridad para que las rutas queden simples:
- Control de acceso: @login_requerido y @requiere_rol('instructor', ...).
- Protección CSRF: cada formulario POST debe traer un token secreto de la sesión.
- Bloqueo por fuerza bruta: 5 intentos fallidos bloquean el RUT por 5 minutos.
"""

import hashlib  # Para la verificación "ficticia" que iguala tiempos de respuesta
import hmac  # Para comparar tokens en tiempo constante
import secrets  # Para generar tokens aleatorios seguros
import time  # Para medir los tiempos de bloqueo
from functools import wraps  # Para crear decoradores que conservan el nombre de la función
from flask import abort, g, redirect, request, session, url_for, flash  # Utilidades de Flask
from dao.instructor_dao import InstructorDao  # Para cargar instructores desde la BD
from dao.recepcionista_dao import RecepcionistaDao  # Para cargar recepcionistas desde la BD
from web.db import obtener_conexion  # Conexión de la petición actual

MAX_INTENTOS = 5  # Intentos fallidos permitidos antes de bloquear
BLOQUEO_SEG = 5 * 60  # Duración del bloqueo: 5 minutos
_intentos: dict[str, list] = {}  # Memoria de intentos: {rut: [cantidad_fallos, bloqueado_hasta]}


# ---------------- Autenticación ----------------

def buscar_trabajador(rut: str):  # Busca un trabajador por RUT en ambas tablas hijas
    conexion = obtener_conexion()  # Obtiene la conexión de la petición
    return InstructorDao(conexion).buscar_por_rut(rut) or RecepcionistaDao(conexion).buscar_por_rut(rut)  # Instructor o Recepcionista


def verificacion_ficticia() -> None:  # Gasta el mismo tiempo que un login real
    """
    Si el RUT no existe se ejecuta igual un hash PBKDF2, para que un atacante
    no pueda saber qué RUT existen midiendo cuánto tarda la respuesta.
    """
    hashlib.pbkdf2_hmac("sha256", b"x", b"salt-ficticio", 260_000)  # Mismo costo que verificar una contraseña real


def trabajador_actual():  # Retorna el trabajador que inició sesión (o None)
    if "trabajador" not in g:  # Si aún no se cargó en esta petición...
        rut = session.get("rut")  # ...lee el RUT guardado en la sesión
        g.trabajador = buscar_trabajador(rut) if rut else None  # ...y lo busca en la BD (si lo borraron, pierde acceso)
    return g.trabajador  # Retorna el trabajador o None


def iniciar_sesion(trabajador) -> None:  # Guarda al trabajador en la sesión
    session.clear()  # Borra la sesión anterior (previene "session fixation")
    session.permanent = True  # Usa la duración configurada (PERMANENT_SESSION_LIFETIME)
    session["rut"] = trabajador.rut  # Guarda solo el RUT (nunca la contraseña ni el hash)
    session["csrf_token"] = secrets.token_urlsafe(32)  # Genera un token CSRF nuevo para esta sesión


# ---------------- Bloqueo por intentos fallidos ----------------

def esta_bloqueado(rut: str) -> int:  # Retorna los segundos de bloqueo restantes (0 si no está bloqueado)
    _, bloqueado_hasta = _intentos.get(rut, [0, 0.0])  # Obtiene el registro del RUT
    return max(int(bloqueado_hasta - time.monotonic()), 0)  # Segundos que faltan, nunca negativo


def registrar_fallo(rut: str) -> None:  # Suma un intento fallido
    fallos, _ = _intentos.get(rut, [0, 0.0])  # Obtiene los fallos acumulados
    fallos += 1  # Suma el fallo actual
    bloqueado_hasta = time.monotonic() + BLOQUEO_SEG if fallos >= MAX_INTENTOS else 0.0  # Bloquea al llegar al máximo
    _intentos[rut] = [0 if bloqueado_hasta else fallos, bloqueado_hasta]  # Al bloquear, el contador se reinicia


def limpiar_intentos(rut: str) -> None:  # Borra los fallos tras un login exitoso
    _intentos.pop(rut, None)  # Elimina el registro del RUT


# ---------------- Protección CSRF ----------------

def token_csrf() -> str:  # Retorna el token CSRF de la sesión (lo crea si falta)
    if "csrf_token" not in session:  # Si la sesión no tiene token...
        session["csrf_token"] = secrets.token_urlsafe(32)  # ...genera uno aleatorio
    return session["csrf_token"]  # Retorna el token para incrustarlo en los formularios


def validar_csrf() -> None:  # Se ejecuta antes de CADA petición (before_request)
    """
    Rechaza con 400 cualquier POST cuyo token no coincida con el de la sesión.
    Evita que otro sitio envíe formularios en nombre del usuario.
    """
    if request.method != "POST":  # Solo se validan los envíos de formularios
        return  # GET no modifica datos
    enviado = request.form.get("csrf_token", "")  # Token que vino en el formulario
    esperado = session.get("csrf_token", "")  # Token guardado en la sesión
    if not esperado or not hmac.compare_digest(enviado, esperado):  # Compara en tiempo constante
        abort(400, description="Formulario expirado o invalido. Recarga la pagina e intenta de nuevo.")  # Rechaza la petición


# ---------------- Decoradores de control de acceso ----------------

def login_requerido(vista):  # Decorador: la vista exige haber iniciado sesión
    @wraps(vista)  # Conserva el nombre de la vista original (Flask lo necesita)
    def envoltura(*args, **kwargs):  # Función que se ejecuta en lugar de la vista
        if trabajador_actual() is None:  # Si no hay sesión válida...
            flash("Debes iniciar sesion para continuar.", "aviso")  # ...avisa al usuario
            return redirect(url_for("auth.login", siguiente=request.path))  # ...y lo envía al login
        return vista(*args, **kwargs)  # Si hay sesión, ejecuta la vista normalmente
    return envoltura  # Retorna la vista protegida


def requiere_rol(*roles: str):  # Decorador con parámetros: roles permitidos
    """
    Ejemplo: @requiere_rol("instructor") -> una recepcionista recibe 403.
    Implementa en la web la regla "la recepcionista no puede crear ni
    modificar clases" (requerimiento 2).
    """
    def decorador(vista):  # Recibe la vista a proteger
        @wraps(vista)  # Conserva el nombre de la vista original
        @login_requerido  # Primero exige sesión iniciada
        def envoltura(*args, **kwargs):  # Función que se ejecuta en lugar de la vista
            if trabajador_actual().rol not in roles:  # Si el rol no está permitido...
                abort(403)  # ...responde 403 Prohibido
            return vista(*args, **kwargs)  # Si está permitido, ejecuta la vista
        return envoltura  # Retorna la vista protegida
    return decorador  # Retorna el decorador configurado
