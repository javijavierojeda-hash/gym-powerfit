import os  # Importa os para leer variables de entorno y armar rutas de archivos
import sqlite3  # Importa el módulo sqlite3 para interactuar con bases de datos SQLite

# Ruta por defecto de la base de datos: el archivo powerfit.db en la misma carpeta que este script
RUTA_POR_DEFECTO = os.path.join(os.path.dirname(os.path.abspath(__file__)), "powerfit.db")


def crear_conexion(ruta: str | None = None) -> sqlite3.Connection:  # Define la función encargada de establecer la conexión
    """
    Crea y retorna una conexión a la base de datos SQLite de PowerFit.

    - La ruta se puede cambiar con el parámetro 'ruta' o con la variable de
      entorno POWERFIT_DB (las pruebas usan ':memory:', una BD temporal en RAM).
    - Habilita las Foreign Keys (claves foráneas), que en SQLite vienen apagadas.
    - Configura row_factory para leer las columnas por nombre: fila["rut"].
    """
    ruta = ruta or os.environ.get("POWERFIT_DB", RUTA_POR_DEFECTO)  # Prioridad: parámetro > variable de entorno > archivo por defecto
    conexion = sqlite3.connect(ruta)  # Crea la conexión a la base de datos (crea el archivo si no existe)
    conexion.row_factory = sqlite3.Row  # Permite acceder a cada columna por su nombre, no solo por posición
    conexion.execute("PRAGMA foreign_keys = ON")  # Habilita el soporte de claves foráneas (integridad referencial)
    return conexion  # Retorna el objeto de conexión para ser usado por los DAOs
