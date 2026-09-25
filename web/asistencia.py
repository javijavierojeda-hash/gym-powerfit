"""
Rutas de asistencia: el instructor ve sus clases y marca a los socios presentes.
"""

from datetime import date  # Para la fecha y el mes actual
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for  # Utilidades de Flask
from dao.asistencia_dao import AsistenciaDao  # DAO de asistencias
from dao.clase_dao import ClaseDao  # DAO de clases
from dao.inscripcion_mensual_dao import InscripcionMensualDao  # Para saber quién está inscrito
from dao.socio_dao import SocioDao  # Para buscar al socio
from model.membresia_vencida_exception import MembresiaVencidaException  # Excepción de membresía vencida
from web.db import obtener_conexion  # Conexión de la petición
from web.seguridad import requiere_rol, trabajador_actual  # Control de acceso

bp = Blueprint("asistencia", __name__, url_prefix="/asistencia")  # Todas las rutas empiezan con /asistencia


@bp.route("/")  # Mis clases
@requiere_rol("instructor")  # Solo instructores
def mis_clases():  # Vista con las clases del instructor
    mes = date.today().strftime("%Y-%m")  # Mes actual
    clases = ClaseDao(obtener_conexion()).listar(mes, trabajador_actual().rut)  # Solo las clases de este instructor
    return render_template("asistencia/mis_clases.html", clases=clases)  # Muestra las clases


@bp.route("/<int:clase_id>", methods=["GET", "POST"])  # Lista de asistencia de una clase
@requiere_rol("instructor")  # Solo instructores
def clase(clase_id: int):  # Vista de la lista de asistencia
    conexion = obtener_conexion()  # Conexión de la petición
    mes = date.today().strftime("%Y-%m")  # Mes actual
    clase_obj = ClaseDao(conexion).buscar_por_id(clase_id, mes)  # Busca la clase
    if clase_obj is None:  # Si no existe...
        abort(404)  # ...responde 404
    instructor = trabajador_actual()  # Instructor que inició sesión
    inscritos = InscripcionMensualDao(conexion).listar_socios_de_clase(clase_id, mes)  # Socios inscritos este mes
    asistencia_dao = AsistenciaDao(conexion)  # DAO de asistencias

    if request.method == "POST":  # Si se marcó o desmarcó a un socio...
        socio = SocioDao(conexion).buscar_por_rut(request.form.get("rut", ""))  # Busca al socio
        if socio is None or socio.rut not in {s.rut for s in inscritos}:  # Solo socios inscritos en ESTA clase
            abort(400)  # Rechaza datos manipulados
        try:  # Intenta registrar
            if request.form.get("accion") == "desmarcar":  # Si se quiere quitar la asistencia...
                if clase_obj.instructor_rut != instructor.rut:  # Solo el instructor de la clase
                    abort(403)  # Bloquea a otros instructores
                asistencia_dao.eliminar(clase_id, socio.rut)  # Borra el registro de hoy
                flash(f"Asistencia de {socio.nombre} quitada.", "exito")  # Confirma
            else:  # Si se quiere marcar presente...
                instructor.marcar_asistencia(clase_obj, socio)  # El modelo valida instructor y membresía vigente
                asistencia_dao.registrar(clase_id, socio.rut, instructor.rut)  # Guarda la asistencia de hoy
                flash(f"{socio.nombre} marcado/a como presente.", "exito")  # Confirma
        except PermissionError as error:  # Si la clase es de otro instructor...
            flash(str(error), "error")  # ...avisa
        except MembresiaVencidaException as error:  # Si la membresía está vencida...
            flash(str(error), "error")  # ...avisa y no registra
        except ValueError as error:  # Si ya estaba registrada...
            flash(str(error), "error")  # ...avisa
        return redirect(url_for("asistencia.clase", clase_id=clase_id))  # Recarga la lista (patrón POST-redirect-GET)

    presentes = asistencia_dao.ruts_presentes(clase_id)  # RUT de los presentes hoy
    return render_template(  # Muestra la lista
        "asistencia/clase.html",
        clase=clase_obj, inscritos=inscritos, presentes=presentes, hoy=date.today(),  # Datos para la plantilla
        es_mia=clase_obj.instructor_rut == instructor.rut,  # Si puede marcar (solo el instructor de la clase)
    )
