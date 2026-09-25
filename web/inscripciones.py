"""
Rutas de inscripciones mensuales: crear, cobrar y anular (solo recepcionista).
"""

from datetime import date  # Para calcular los meses disponibles
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for  # Utilidades de Flask
from dao.clase_dao import ClaseDao  # Para listar las clases con cupos
from dao.inscripcion_mensual_dao import InscripcionMensualDao  # Para guardar y leer inscripciones
from dao.socio_dao import SocioDao  # Para buscar al socio
from model.cupo_lleno_exception import CupoLlenoException  # Excepción de cupo lleno
from model.detalle_clase_reservada import DetalleClaseReservada  # Detalle de cada clase reservada
from model.inscripcion_mensual import InscripcionMensual  # La transacción del negocio
from web.db import obtener_conexion  # Conexión de la petición
from web.seguridad import requiere_rol, trabajador_actual  # Control de acceso

bp = Blueprint("inscripciones", __name__, url_prefix="/inscripciones")  # Todas las rutas empiezan con /inscripciones


def meses_disponibles() -> list[str]:  # Meses en que se puede inscribir: el actual y el siguiente
    hoy = date.today()  # Fecha de hoy
    siguiente = date(hoy.year + (hoy.month == 12), hoy.month % 12 + 1, 1)  # Primer día del mes siguiente
    return [hoy.strftime("%Y-%m"), siguiente.strftime("%Y-%m")]  # Ej: ["2026-09", "2026-10"]


@bp.route("/")  # Listado de inscripciones de un mes
@requiere_rol("recepcionista")  # Solo la recepcionista
def lista():  # Vista del listado
    mes = request.args.get("mes", date.today().strftime("%Y-%m"))  # Mes a mostrar (por defecto, el actual)
    try:  # Valida el formato del mes
        date.fromisoformat(mes + "-01")  # Si "mes" no es AAAA-MM válido, lanza ValueError
    except ValueError:  # Mes inválido...
        abort(400)  # ...responde 400
    inscripciones = InscripcionMensualDao(obtener_conexion()).listar(mes)  # Inscripciones del mes
    return render_template("inscripciones/lista.html", inscripciones=inscripciones, mes=mes)  # Muestra la tabla


@bp.route("/nueva", methods=["GET", "POST"])  # Crear una inscripción mensual
@requiere_rol("recepcionista")  # Solo la recepcionista (requerimiento 2)
def nueva():  # Vista del formulario de inscripción
    conexion = obtener_conexion()  # Conexión de la petición
    meses = meses_disponibles()  # Meses permitidos
    rut = request.values.get("rut", "")  # RUT del socio (desde la URL o el formulario)
    mes = request.values.get("mes", meses[0])  # Mes elegido (por defecto, el actual)
    if mes not in meses:  # Si el mes no está permitido...
        abort(400)  # ...se rechaza (no se confía en datos del navegador)
    socio = SocioDao(conexion).buscar_por_rut(rut) if rut else None  # Busca al socio si se indicó RUT
    clases = ClaseDao(conexion).listar(mes)  # Clases con los cupos de ese mes
    dao = InscripcionMensualDao(conexion)  # DAO de inscripciones
    existente = dao.buscar(socio.rut, mes) if socio else None  # Inscripción ya existente del socio en ese mes

    if request.method == "POST" and socio and not existente:  # Si se envió el formulario válido...
        ids = {int(x) for x in request.form.getlist("clases") if x.isdigit()}  # Ids de clases marcadas (solo números)
        seleccion = [c for c in clases if c.id in ids]  # Toma solo clases que existen de verdad
        if not seleccion:  # Regla 1..* del UML
            flash("Debes reservar al menos una clase.", "error")  # Avisa el error
        else:  # Si hay clases seleccionadas...
            inscripcion = InscripcionMensual(socio, mes)  # Crea la inscripción en memoria
            try:  # Intenta agregar las clases y guardar
                for clase in seleccion:  # Recorre las clases elegidas
                    inscripcion.agregar_clase(DetalleClaseReservada(clase))  # Lanza CupoLlenoException si está llena
                dao.guardar(inscripcion, trabajador_actual().rut)  # Guarda todo (revisa el cupo de nuevo en la BD)
            except CupoLlenoException as error:  # Si alguna clase no tenía cupo...
                flash(str(error) + ". La inscripcion NO se guardo.", "error")  # ...avisa y no guarda nada
            except ValueError as error:  # Otros problemas (duplicado, etc.)
                flash(str(error), "error")  # Avisa el error
            else:  # Si todo salió bien...
                flash(f"Inscripcion de {socio.nombre} guardada: {len(seleccion)} clase(s).", "exito")  # ...confirma
                return redirect(url_for("socios.ficha", rut=socio.rut))  # ...y muestra la ficha del socio
        clases = ClaseDao(conexion).listar(mes)  # Recarga los cupos por si cambiaron

    return render_template(  # Muestra el formulario
        "inscripciones/nueva.html",
        socio=socio, rut=rut, mes=mes, meses=meses, clases=clases, existente=existente,  # Datos para la plantilla
    )


@bp.route("/<int:inscripcion_id>/cobrar", methods=["POST"])  # Cobrar la mensualidad
@requiere_rol("recepcionista")  # Solo la recepcionista cobra (requerimiento 2)
def cobrar(inscripcion_id: int):  # Vista que procesa el cobro
    dao = InscripcionMensualDao(obtener_conexion())  # DAO de inscripciones
    inscripcion = dao.buscar_por_id(inscripcion_id)  # Busca la inscripción
    if inscripcion is None:  # Si no existe...
        abort(404)  # ...responde 404
    recepcionista = trabajador_actual()  # La recepcionista que cobra
    try:  # Intenta cobrar
        total = recepcionista.cobrar_mensualidad(inscripcion)  # El modelo valida, marca pagada y renueva membresía
        dao.registrar_pago(inscripcion, total, recepcionista.rut)  # Guarda el pago y la membresía en una transacción
    except ValueError as error:  # Si ya estaba pagada o el mes terminó...
        flash(str(error), "error")  # ...avisa el problema
    else:  # Si el cobro funcionó...
        flash(f"Cobro registrado por ${total:,}. Membresia vigente hasta {inscripcion.socio.membresia.fecha_vencimiento:%d-%m-%Y}.".replace(",", "."), "exito")  # Confirma
    return redirect(url_for("socios.ficha", rut=inscripcion.socio.rut))  # Vuelve a la ficha del socio


@bp.route("/<int:inscripcion_id>/anular", methods=["POST"])  # Anular una inscripción no pagada
@requiere_rol("recepcionista")  # Solo la recepcionista
def anular(inscripcion_id: int):  # Vista que procesa la anulación
    dao = InscripcionMensualDao(obtener_conexion())  # DAO de inscripciones
    inscripcion = dao.buscar_por_id(inscripcion_id)  # Busca la inscripción
    if inscripcion is None:  # Si no existe...
        abort(404)  # ...responde 404
    try:  # Intenta anular
        dao.eliminar(inscripcion_id)  # Solo borra si no está pagada (los detalles se borran en cascada)
        flash("Inscripcion anulada: los cupos quedaron liberados.", "exito")  # Confirma
    except ValueError as error:  # Si estaba pagada...
        flash(str(error), "error")  # ...avisa que no se puede
    return redirect(url_for("socios.ficha", rut=inscripcion.socio.rut))  # Vuelve a la ficha del socio
