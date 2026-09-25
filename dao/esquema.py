"""
Crea el esquema COMPLETO de la base de datos en el orden correcto.

El orden importa por las llaves foráneas: primero las tablas "padre"
(trabajadores, clases, socios) y después las que las referencian.
"""

from dao.instructor_dao import InstructorDao  # Crea trabajadores + instructores
from dao.recepcionista_dao import RecepcionistaDao  # Crea recepcionistas
from dao.yoga_dao import YogaDao  # Crea clases + yoga
from dao.spinning_dao import SpinningDao  # Crea spinning
from dao.crossfit_dao import CrossfitDao  # Crea crossfit
from dao.socio_dao import SocioDao  # Crea socios
from dao.membresia_dao import MembresiaDao  # Crea membresias
from dao.inscripcion_mensual_dao import InscripcionMensualDao  # Crea inscripciones_mensuales
from dao.detalle_clase_reservada_dao import DetalleClaseReservadaDao  # Crea detalles_clase_reservada
from dao.asistencia_dao import AsistenciaDao  # Crea asistencias
from dao.suplemento_dao import SuplementoDao  # Crea suplementos + ventas_suplemento
from dao.indicador_dao import IndicadorDao  # Crea indicadores

# Lista ordenada de DAOs cuyo crear_tabla() se debe ejecutar
DAOS_EN_ORDEN = (
    InstructorDao, RecepcionistaDao,  # 1) Trabajadores (herencia tabla por tipo)
    YogaDao, SpinningDao, CrossfitDao,  # 2) Clases (herencia tabla por tipo)
    SocioDao, MembresiaDao,  # 3) Socios y su membresía (composición)
    InscripcionMensualDao, DetalleClaseReservadaDao,  # 4) La transacción y su detalle
    AsistenciaDao, SuplementoDao, IndicadorDao,  # 5) Asistencia, suplementos y dólar
)


def crear_esquema(conexion) -> list[str]:  # Crea todas las tablas y retorna sus nombres
    for clase_dao in DAOS_EN_ORDEN:  # Recorre los DAOs en orden
        clase_dao(conexion).crear_tabla()  # Instancia el DAO con la conexión y crea su(s) tabla(s)
    filas = conexion.execute(  # Consulta al catálogo de SQLite qué tablas existen (como el main del profe)
        "SELECT name FROM sqlite_master WHERE type = 'table' AND name != 'sqlite_sequence' ORDER BY name"  # Excluye la tabla interna
    ).fetchall()  # Lista de filas
    return [f["name"] for f in filas]  # Retorna solo los nombres
