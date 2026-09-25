"""
Rutas de socios: listar, registrar y ver ficha (solo recepcionista).
"""

from datetime import date  # Para el mes actual
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for  # Utilidades de Flask
from dao.inscripcion_mensual_dao import InscripcionMensualDao  # Para ver la inscripción del mes
from dao.socio_dao import SocioDao  # Para leer y guardar socios
from web.db import obtener_conexion  # Conexión de la petición
from web.seguridad import requiere_rol, trabajador_actual  # Control de acceso

bp = Blueprint("socios", __name__, url_prefix="/socios")  # Todas las rutas empiezan con /socios


@bp.route("/")  # Listado de socios
@requiere_rol("recepcionista")  # Solo la recepcionista gestiona socios
def lista():  # Vista del listado
    filtro = request.args.get("q", "")[:50]  # Texto de búsqueda (máximo 50 caracteres)
    socios = SocioDao(obtener_conexion()).listar(filtro)  # Busca socios por nombre o RUT
    return render_template("socios/lista.html", socios=socios, filtro=filtro)  # Muestra la tabla


@bp.route("/nuevo", methods=["GET", "POST"])  # Registro de socio nuevo
@requiere_rol("recepcionista")  # Solo la recepcionista inscribe socios (requerimiento 2)
def nuevo():  # Vista del formulario
    datos = {"rut": "", "nombre": ""}  # Valores del formulario (vacíos al inicio)
    if request.method == "POST":  # Si se envió el formulario...
        datos = {"rut": request.form.get("rut", "").strip(), "nombre": request.form.get("nombre", "").strip()[:80]}  # Lee y limita los datos
        dao = SocioDao(obtener_conexion())  # DAO de socios
        try:  # Intenta crear el socio
            socio = trabajador_actual().inscribir_socio(datos["rut"], datos["nombre"])  # El modelo valida el RUT (requerimiento 3)
            if dao.existe(socio.rut):  # Si el RUT ya está registrado...
                raise ValueError(f"Ya existe un socio con RUT {socio.rut_formateado}")  # ...no se duplica
            dao.insertar(socio)  # Guarda socio + membresía en una transacción
        except ValueError as error:  # Si el RUT es inválido o está repetido...
            flash(str(error), "error")  # ...muestra el problema
            return render_template("socios/nuevo.html", datos=datos), 400  # ...y vuelve al formulario con los datos
        flash(f"Socio {socio.nombre} registrado. Ahora inscribe sus clases del mes.", "exito")  # Confirma el registro
        return redirect(url_for("inscripciones.nueva", rut=socio.rut))  # Lleva directo a la inscripción mensual
    return render_template("socios/nuevo.html", datos=datos)  # GET: muestra el formulario


@bp.route("/<rut>")  # Ficha del socio
@requiere_rol("recepcionista")  # Solo la recepcionista
def ficha(rut: str):  # Vista de la ficha
    conexion = obtener_conexion()  # Conexión de la petición
    socio = SocioDao(conexion).buscar_por_rut(rut)  # Busca el socio
    if socio is None:  # Si no existe...
        abort(404)  # ...responde 404
    inscripciones = InscripcionMensualDao(conexion).listar_por_socio(socio.rut)  # Historial de inscripciones (más reciente primero)
    return render_template("socios/ficha.html", socio=socio, inscripciones=inscripciones, hoy=date.today())  # Muestra la ficha
