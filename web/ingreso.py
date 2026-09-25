"""
Control de ingreso al gimnasio (requerimiento 5): se ingresa el RUT y el
sistema indica si el socio puede pasar o si tiene la membresía vencida.
"""

from flask import Blueprint, render_template, request  # Utilidades de Flask
from dao.socio_dao import SocioDao  # Para buscar al socio
from model.membresia_vencida_exception import MembresiaVencidaException  # Excepción de membresía vencida
from model.validaciones import es_rut_valido  # Validación del RUT
from web.db import obtener_conexion  # Conexión de la petición
from web.seguridad import login_requerido  # Control de acceso

bp = Blueprint("ingreso", __name__, url_prefix="/ingreso")  # Todas las rutas empiezan con /ingreso


@bp.route("/", methods=["GET", "POST"])  # Pantalla de control de ingreso
@login_requerido  # Cualquier trabajador puede controlar la entrada
def control():  # Vista del control de ingreso
    resultado = None  # Resultado a mostrar (None = aún no se consulta)
    if request.method == "POST":  # Si se envió un RUT...
        rut = request.form.get("rut", "")  # Lee el RUT
        if not es_rut_valido(rut):  # Si el RUT es inválido...
            resultado = {"estado": "invalido", "mensaje": "El RUT ingresado no es valido."}  # ...lo informa
        else:  # Si el RUT es válido...
            socio = SocioDao(obtener_conexion()).buscar_por_rut(rut)  # ...busca al socio
            if socio is None:  # Si no está registrado...
                resultado = {"estado": "invalido", "mensaje": "No existe un socio con ese RUT."}  # ...lo informa
            else:  # Si existe...
                try:  # Revisa la membresía
                    socio.puede_ingresar()  # Lanza MembresiaVencidaException si está vencida
                    resultado = {"estado": "ok", "socio": socio}  # Puede ingresar
                except MembresiaVencidaException as error:  # Si está vencida...
                    resultado = {"estado": "vencida", "socio": socio, "mensaje": str(error)}  # ...se niega el ingreso
    return render_template("ingreso.html", resultado=resultado)  # Muestra la pantalla con el resultado
