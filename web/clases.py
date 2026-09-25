"""
Rutas de clases.
- Ver el listado: cualquier trabajador.
- Crear, editar y eliminar: SOLO el instructor (requerimiento 2: la
  recepcionista no puede crear ni modificar clases -> recibe 403).
"""

import sqlite3  # Para reconocer el error de llave foránea al eliminar
from datetime import date, time  # Para el mes actual y validar la hora
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for  # Utilidades de Flask
from dao.clase_dao import ClaseDao  # DAO genérico de clases
from dao.crossfit_dao import CrossfitDao  # DAO de Crossfit
from dao.instructor_dao import InstructorDao  # Para mostrar el nombre del instructor
from dao.spinning_dao import SpinningDao  # DAO de Spinning
from dao.yoga_dao import YogaDao  # DAO de Yoga
from model.clase import DIAS_SEMANA  # Días válidos
from model.spinning import Spinning  # Para saber si una clase es Spinning
from web.db import obtener_conexion  # Conexión de la petición
from web.seguridad import login_requerido, requiere_rol, trabajador_actual  # Control de acceso

bp = Blueprint("clases", __name__, url_prefix="/clases")  # Todas las rutas empiezan con /clases

DAO_POR_TIPO = {"yoga": YogaDao, "spinning": SpinningDao, "crossfit": CrossfitDao}  # Qué DAO guarda cada tipo


def _leer_formulario():  # Lee y valida día y hora del formulario
    dia = request.form.get("dia", "")  # Día elegido
    if dia not in DIAS_SEMANA:  # Solo se aceptan días de la lista
        raise ValueError("Selecciona un dia valido.")  # Rechaza valores manipulados
    try:  # Intenta convertir la hora
        hora = time.fromisoformat(request.form.get("hora", ""))  # Convierte "HH:MM" en objeto time
    except ValueError:  # Si el formato es inválido...
        raise ValueError("Ingresa una hora valida (HH:MM).")  # ...avisa con un mensaje claro
    return dia, hora.replace(second=0, microsecond=0)  # Retorna día y hora sin segundos


def _clase_propia(clase_id: int):  # Busca una clase y verifica que sea del instructor actual
    clase = ClaseDao(obtener_conexion()).buscar_por_id(clase_id)  # Busca la clase
    if clase is None:  # Si no existe...
        abort(404)  # ...responde 404
    if clase.instructor_rut != trabajador_actual().rut:  # Si es de otro instructor...
        abort(403)  # ...no puede modificarla
    return clase  # Retorna la clase


@bp.route("/")  # Listado de clases
@login_requerido  # Cualquier trabajador con sesión puede verlas
def lista():  # Vista del listado
    conexion = obtener_conexion()  # Conexión de la petición
    mes = date.today().strftime("%Y-%m")  # Mes actual
    clases = ClaseDao(conexion).listar(mes)  # Todas las clases con cupos del mes
    instructores = {i.rut: i.nombre for i in InstructorDao(conexion).listar()}  # Diccionario RUT -> nombre
    return render_template("clases/lista.html", clases=clases, instructores=instructores, mes=mes)  # Muestra la tabla


@bp.route("/nueva", methods=["GET", "POST"])  # Crear clase
@requiere_rol("instructor")  # SOLO instructor: la recepcionista recibe 403
def nueva():  # Vista del formulario de nueva clase
    if request.method == "POST":  # Si se envió el formulario...
        tipo = request.form.get("tipo", "")  # Tipo de clase elegido
        try:  # Intenta crear la clase
            if tipo not in DAO_POR_TIPO:  # Valida el tipo
                raise ValueError("Selecciona un tipo de clase valido.")  # Rechaza tipos inexistentes
            dia, hora = _leer_formulario()  # Lee y valida día y hora
            clase = trabajador_actual().crear_clase(tipo, dia, hora)  # El instructor crea la clase (queda asignada a él)
            if isinstance(clase, Spinning):  # Si es Spinning...
                clase.bicicletas_operativas = int(request.form.get("bicicletas", Spinning.CUPO_MAXIMO))  # ...lee las bicicletas operativas
            DAO_POR_TIPO[tipo](obtener_conexion()).insertar(clase)  # Guarda con el DAO de su tipo
        except ValueError as error:  # Si hubo datos inválidos...
            flash(str(error), "error")  # ...avisa
            return render_template("clases/form.html", clase=None, dias=DIAS_SEMANA), 400  # ...y vuelve al formulario
        flash(f"Clase {clase} creada.", "exito")  # Confirma
        return redirect(url_for("clases.lista"))  # Vuelve al listado
    return render_template("clases/form.html", clase=None, dias=DIAS_SEMANA)  # GET: formulario vacío


@bp.route("/<int:clase_id>/editar", methods=["GET", "POST"])  # Editar clase
@requiere_rol("instructor")  # SOLO instructor
def editar(clase_id: int):  # Vista de edición
    clase = _clase_propia(clase_id)  # Solo el instructor dueño puede editarla
    if request.method == "POST":  # Si se envió el formulario...
        conexion = obtener_conexion()  # Conexión de la petición
        try:  # Intenta actualizar
            dia, hora = _leer_formulario()  # Lee y valida día y hora
            ClaseDao(conexion).actualizar_horario(clase.id, dia, hora)  # Guarda el nuevo horario
            if isinstance(clase, Spinning):  # Si es Spinning...
                clase.bicicletas_operativas = int(request.form.get("bicicletas", clase.bicicletas_operativas))  # ...valida con el setter del modelo
                SpinningDao(conexion).actualizar_bicicletas(clase.id, clase.bicicletas_operativas)  # ...y guarda las bicicletas
        except ValueError as error:  # Si hubo datos inválidos...
            flash(str(error), "error")  # ...avisa
            return render_template("clases/form.html", clase=clase, dias=DIAS_SEMANA), 400  # ...y vuelve al formulario
        flash("Clase actualizada.", "exito")  # Confirma
        return redirect(url_for("clases.lista"))  # Vuelve al listado
    return render_template("clases/form.html", clase=clase, dias=DIAS_SEMANA)  # GET: formulario con los datos actuales


@bp.route("/<int:clase_id>/eliminar", methods=["POST"])  # Eliminar clase
@requiere_rol("instructor")  # SOLO instructor
def eliminar(clase_id: int):  # Vista que procesa la eliminación
    clase = _clase_propia(clase_id)  # Solo el instructor dueño puede eliminarla
    try:  # Intenta eliminar
        ClaseDao(obtener_conexion()).eliminar(clase.id)  # Borra la clase
        flash(f"Clase {clase} eliminada.", "exito")  # Confirma
    except sqlite3.IntegrityError:  # Si tiene reservas, la llave foránea lo impide
        flash("No se puede eliminar: la clase tiene socios inscritos.", "error")  # Avisa
    return redirect(url_for("clases.lista"))  # Vuelve al listado
