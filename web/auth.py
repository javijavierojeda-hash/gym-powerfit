"""
Rutas de autenticación: iniciar y cerrar sesión.
"""

from flask import Blueprint, flash, redirect, render_template, request, session, url_for  # Utilidades de Flask
from model.validaciones import es_rut_valido, limpiar_rut  # Validación y normalización del RUT
from web.seguridad import (  # Controles de seguridad
    buscar_trabajador, esta_bloqueado, iniciar_sesion, limpiar_intentos,
    registrar_fallo, trabajador_actual, verificacion_ficticia,
)

bp = Blueprint("auth", __name__)  # Crea el grupo de rutas "auth"

MENSAJE_ERROR = "RUT o contrasena incorrectos."  # Mensaje genérico: no revela si falló el RUT o la clave


@bp.route("/login", methods=["GET", "POST"])  # Ruta del formulario de login (muestra y procesa)
def login():  # Vista de inicio de sesión
    if trabajador_actual():  # Si ya hay una sesión activa...
        return redirect(url_for("panel.inicio"))  # ...lo envía directo al panel
    if request.method == "POST":  # Si se envió el formulario...
        rut = limpiar_rut(request.form.get("rut", ""))  # Normaliza el RUT ingresado
        password = request.form.get("password", "")  # Lee la contraseña (nunca se guarda ni se imprime)
        segundos = esta_bloqueado(rut)  # Revisa si el RUT está bloqueado por intentos fallidos
        if segundos:  # Si está bloqueado...
            flash(f"Demasiados intentos fallidos. Intenta de nuevo en {segundos // 60 + 1} minuto(s).", "error")  # ...avisa
            return render_template("login.html", rut=request.form.get("rut", "")), 429  # 429 = demasiadas solicitudes
        trabajador = buscar_trabajador(rut) if es_rut_valido(rut) else None  # Busca al trabajador solo si el RUT es válido
        if trabajador is None:  # Si no existe...
            verificacion_ficticia()  # ...gasta el mismo tiempo que un login real (no revela qué RUT existen)
        if trabajador is not None and trabajador.login(password):  # Si existe y la contraseña es correcta...
            limpiar_intentos(rut)  # ...borra los fallos acumulados
            iniciar_sesion(trabajador)  # ...inicia la sesión
            flash(f"Bienvenido/a, {trabajador.nombre}.", "exito")  # ...da la bienvenida
            siguiente = request.args.get("siguiente", "")  # Página que el usuario quería ver antes del login
            if siguiente.startswith("/") and not siguiente.startswith("//"):  # Solo rutas internas (evita "open redirect")
                return redirect(siguiente)  # Lo lleva a la página que pedía
            return redirect(url_for("panel.inicio"))  # Si no, al panel principal
        registrar_fallo(rut)  # Suma un intento fallido
        flash(MENSAJE_ERROR, "error")  # Muestra el mensaje genérico
        return render_template("login.html", rut=request.form.get("rut", "")), 401  # 401 = no autenticado
    return render_template("login.html", rut="")  # GET: muestra el formulario vacío


@bp.route("/logout", methods=["POST"])  # Cerrar sesión solo por POST (un enlace externo no puede cerrarla)
def logout():  # Vista de cierre de sesión
    session.clear()  # Borra toda la información de la sesión
    flash("Sesion cerrada correctamente.", "exito")  # Confirma al usuario
    return redirect(url_for("auth.login"))  # Vuelve al login
