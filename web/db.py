"""
Manejo de la conexión a la base de datos dentro de la aplicación web.

Cada petición HTTP abre UNA conexión (guardada en flask.g) y la cierra al
terminar. Así nunca se comparten conexiones entre usuarios simultáneos.
"""

from flask import current_app, g  # current_app: la app activa; g: almacén temporal por petición
import conectar  # Módulo de conexión del proyecto (igual que en la consola)


def obtener_conexion():  # Retorna la conexión de la petición actual (la crea si no existe)
    if "conexion" not in g:  # Si esta petición aún no abrió una conexión...
        g.conexion = conectar.crear_conexion(current_app.config["DATABASE"])  # ...la abre con la ruta configurada
    return g.conexion  # Retorna la conexión


def cerrar_conexion(_error=None) -> None:  # Cierra la conexión al terminar la petición
    conexion = g.pop("conexion", None)  # Saca la conexión de g (None si no se abrió)
    if conexion is not None:  # Si había una conexión...
        conexion.close()  # ...la cierra para liberar el archivo de la BD
