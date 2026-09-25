"""
Panel principal: resumen del gimnasio según el rol del trabajador.
"""

from datetime import date  # Para obtener el mes actual
from flask import Blueprint, render_template  # Utilidades de Flask
from dao.clase_dao import ClaseDao  # Para listar clases
from dao.socio_dao import SocioDao  # Para contar socios
from web.db import obtener_conexion  # Conexión de la petición
from web.seguridad import login_requerido, trabajador_actual  # Control de acceso

bp = Blueprint("panel", __name__)  # Crea el grupo de rutas "panel"


@bp.route("/")  # Página de inicio
@login_requerido  # Requiere sesión iniciada
def inicio():  # Vista del panel
    conexion = obtener_conexion()  # Conexión de la petición
    usuario = trabajador_actual()  # Trabajador que inició sesión
    mes = date.today().strftime("%Y-%m")  # Mes actual
    socios = SocioDao(conexion).listar()  # Todos los socios con su membresía
    vigentes = sum(1 for s in socios if s.membresia.esta_vigente())  # Cuenta los socios con membresía vigente
    fila = conexion.execute(  # Resumen de inscripciones e ingresos del mes
        """SELECT COUNT(*) AS total, COALESCE(SUM(monto_pagado), 0) AS ingresos, SUM(pagada = 0) AS pendientes
           FROM inscripciones_mensuales WHERE mes = ?""",  # Consulta parametrizada
        (mes,),  # Mes actual
    ).fetchone()  # Una sola fila con los totales
    instructor_rut = usuario.rut if usuario.rol == "instructor" else None  # El instructor ve solo sus clases
    clases = ClaseDao(conexion).listar(mes, instructor_rut)  # Clases con sus cupos del mes
    return render_template(  # Renderiza el panel con los datos
        "panel.html",
        mes=mes, total_socios=len(socios), vigentes=vigentes,  # Datos de socios
        inscripciones=fila["total"], ingresos=fila["ingresos"], pendientes=fila["pendientes"] or 0,  # Datos del mes
        clases=clases,  # Clases a mostrar
    )
