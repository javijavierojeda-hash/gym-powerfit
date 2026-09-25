"""
Rutas de suplementos: precios en CLP según el dólar del día y venta en mesón
(solo recepcionista, requerimiento 6).
"""

from flask import Blueprint, flash, redirect, render_template, request, url_for  # Utilidades de Flask
from dao.suplemento_dao import SuplementoDao  # DAO de suplementos
from services.dolar_service import DolarService  # Servicio del dólar del día
from web.db import obtener_conexion  # Conexión de la petición
from web.seguridad import requiere_rol, trabajador_actual  # Control de acceso

bp = Blueprint("suplementos", __name__, url_prefix="/suplementos")  # Todas las rutas empiezan con /suplementos


@bp.route("/")  # Catálogo y venta
@requiere_rol("recepcionista")  # Solo la recepcionista vende
def lista():  # Vista del catálogo
    conexion = obtener_conexion()  # Conexión de la petición
    cotizacion = DolarService(conexion).obtener_cotizacion()  # Dólar del día (API, respaldo o por defecto)
    dao = SuplementoDao(conexion)  # DAO de suplementos
    suplementos = dao.listar()  # Todos los productos
    for s in suplementos:  # Recorre los productos...
        s.actualizar_precio(cotizacion.valor)  # ...y recalcula su precio en pesos con el dólar de hoy
    dao.actualizar_precios(suplementos)  # Guarda los precios recalculados
    return render_template(  # Muestra el catálogo
        "suplementos.html", suplementos=suplementos, cotizacion=cotizacion, ventas=dao.listar_ventas(),  # Datos para la plantilla
    )


@bp.route("/vender", methods=["POST"])  # Procesa una venta
@requiere_rol("recepcionista")  # Solo la recepcionista
def vender():  # Vista de venta
    conexion = obtener_conexion()  # Conexión de la petición
    dao = SuplementoDao(conexion)  # DAO de suplementos
    suplemento = dao.buscar(request.form.get("codigo", ""))  # Busca el producto
    try:  # Intenta vender
        if suplemento is None:  # Si el producto no existe...
            raise ValueError("Producto no encontrado.")  # ...avisa
        cantidad = int(request.form.get("cantidad", "0"))  # Convierte la cantidad a número (ValueError si no es número)
        valor_dolar = DolarService(conexion).obtener_valor()  # Dólar del día
        suplemento.actualizar_precio(valor_dolar)  # Precio en CLP de hoy
        total = trabajador_actual().vender_suplemento(suplemento, cantidad)  # El modelo valida cantidad y stock
        dao.registrar_venta(suplemento, cantidad, total, valor_dolar, trabajador_actual().rut)  # Descuenta stock y registra (atómico)
    except ValueError as error:  # Cantidad inválida, sin stock, etc.
        flash(str(error) if "invalid literal" not in str(error) else "Ingresa una cantidad valida.", "error")  # Mensaje claro
    else:  # Si la venta funcionó...
        flash(f"Venta registrada: {cantidad} x {suplemento.nombre} = ${total:,}".replace(",", "."), "exito")  # Confirma
    return redirect(url_for("suplementos.lista"))  # Vuelve al catálogo
