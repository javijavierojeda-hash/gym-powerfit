"""
Carga datos de ejemplo en la base de datos para poder probar y mostrar el
prototipo. Es seguro ejecutarlo varias veces: si ya hay datos, no duplica nada.

Uso:  python seed.py
"""

import calendar  # Librería estándar para calcular el último día de cada mes
from datetime import date, time, timedelta  # Tipos de fecha, hora y diferencia de tiempo
import conectar  # Módulo de conexión a la base de datos
from dao.esquema import crear_esquema  # Función que crea todas las tablas
from dao.instructor_dao import InstructorDao  # DAO de instructores
from dao.recepcionista_dao import RecepcionistaDao  # DAO de recepcionistas
from dao.yoga_dao import YogaDao  # DAO de clases de yoga
from dao.spinning_dao import SpinningDao  # DAO de clases de spinning
from dao.crossfit_dao import CrossfitDao  # DAO de clases de crossfit
from dao.clase_dao import ClaseDao  # DAO genérico de clases (lectura)
from dao.socio_dao import SocioDao  # DAO de socios
from dao.inscripcion_mensual_dao import InscripcionMensualDao  # DAO de inscripciones
from dao.suplemento_dao import SuplementoDao  # DAO de suplementos
from model.trabajador import Trabajador  # Para generar los hash de contraseña
from model.instructor import Instructor  # Clase Instructor
from model.recepcionista import Recepcionista  # Clase Recepcionista
from model.socio import Socio  # Clase Socio
from model.inscripcion_mensual import InscripcionMensual  # Clase InscripcionMensual
from model.detalle_clase_reservada import DetalleClaseReservada  # Clase DetalleClaseReservada
from model.suplemento import Suplemento  # Clase Suplemento
from model.validaciones import calcular_dv  # Para armar RUT de ejemplo válidos
from services.dolar_service import DolarService  # Servicio del dólar del día

# Contraseñas de DEMOSTRACIÓN (solo para el prototipo; en producción se cambian)
PASSWORD_INSTRUCTOR = "Instructor123!"  # Contraseña de los instructores de ejemplo
PASSWORD_RECEPCION = "Recepcion123!"  # Contraseña de la recepcionista de ejemplo

# Números de RUT de ejemplo (el dígito verificador se calcula con módulo 11)
_SOCIOS = [
    (12345678, "Ana Perez"), (15678432, "Pedro Gonzalez"), (17234987, "Carla Diaz"),
    (18456123, "Matias Fuentes"), (19876543, "Josefa Morales"), (20123456, "Benjamin Rojas"),
    (16345789, "Isidora Silva"), (14987321, "Tomas Contreras"), (21456789, "Martina Lopez"),
    (13579246, "Vicente Araya"), (24681357, "Florencia Castro"), (19283746, "Agustin Reyes"),
]  # Lista de (número de RUT, nombre)


def _rut(numero: int) -> str:  # Arma un RUT válido a partir del número
    return f"{numero}-{calcular_dv(str(numero))}"  # Ej: 12345678 -> "12345678-5"


def cargar_datos_demo(conexion) -> bool:  # Carga todos los datos de ejemplo
    """
    Retorna True si cargó datos, o False si la BD ya tenía datos.
    """
    crear_esquema(conexion)  # Asegura que existan todas las tablas
    if InstructorDao(conexion).listar():  # Si ya hay instructores, la BD ya tiene datos...
        return False  # ...no se carga nada para no duplicar

    hoy = date.today()  # Fecha actual
    mes = hoy.strftime("%Y-%m")  # Mes actual en formato AAAA-MM
    fin_mes = date(hoy.year, hoy.month, calendar.monthrange(hoy.year, hoy.month)[1])  # Último día del mes actual
    fin_mes_anterior = hoy.replace(day=1) - timedelta(days=1)  # Último día del mes anterior

    # 1) Trabajadores
    camila = Instructor("11111111-1", "Camila Rojas", Trabajador.generar_hash(PASSWORD_INSTRUCTOR))  # Instructora 1
    diego = Instructor("17654321-3", "Diego Munoz", Trabajador.generar_hash(PASSWORD_INSTRUCTOR))  # Instructor 2
    valentina = Recepcionista("22222222-2", "Valentina Soto", Trabajador.generar_hash(PASSWORD_RECEPCION))  # Recepcionista
    InstructorDao(conexion).insertar(camila)  # Guarda a Camila
    InstructorDao(conexion).insertar(diego)  # Guarda a Diego
    RecepcionistaDao(conexion).insertar(valentina)  # Guarda a Valentina

    # 2) Clases (las crea el instructor: la recepcionista no puede)
    yoga_lunes = camila.crear_clase("yoga", "lunes", time(9, 0))  # Yoga lunes 09:00
    yoga_miercoles = camila.crear_clase("yoga", "miercoles", time(19, 0))  # Yoga miércoles 19:00
    crossfit_viernes = camila.crear_clase("crossfit", "viernes", time(18, 30))  # Crossfit viernes 18:30 (se llenará)
    spinning_martes = diego.crear_clase("spinning", "martes", time(18, 0))  # Spinning martes 18:00
    spinning_martes.bicicletas_operativas = 13  # Dos bicicletas en mantención: 13 cupos
    spinning_jueves = diego.crear_clase("spinning", "jueves", time(7, 30))  # Spinning jueves 07:30
    crossfit_miercoles = diego.crear_clase("crossfit", "miercoles", time(20, 0))  # Crossfit miércoles 20:00
    for clase, dao in (  # Guarda cada clase con el DAO de su tipo
        (yoga_lunes, YogaDao), (yoga_miercoles, YogaDao), (crossfit_viernes, CrossfitDao),
        (spinning_martes, SpinningDao), (spinning_jueves, SpinningDao), (crossfit_miercoles, CrossfitDao),
    ):
        dao(conexion).insertar(clase)  # Inserta la clase (asigna su id)

    # 3) Socios: los 2 últimos quedan con membresía vencida el mes anterior
    socio_dao = SocioDao(conexion)  # DAO de socios
    socios = []  # Lista de socios creados
    for indice, (numero, nombre) in enumerate(_SOCIOS):  # Recorre la lista de ejemplo
        if indice >= len(_SOCIOS) - 2:  # Los dos últimos socios...
            socio = Socio(_rut(numero), nombre, fin_mes_anterior.replace(day=1), fin_mes_anterior)  # ...con membresía vencida
        else:  # El resto...
            socio = valentina.inscribir_socio(_rut(numero), nombre)  # ...se inscribe normalmente (pendiente de pago)
        socio_dao.insertar(socio)  # Guarda el socio con su membresía
        socios.append(socio)  # Lo agrega a la lista

    # 4) Inscripciones del mes: los 10 primeros llenan el Crossfit del viernes
    inscripcion_dao = InscripcionMensualDao(conexion)  # DAO de inscripciones
    clase_dao = ClaseDao(conexion)  # DAO para releer las clases con inscritos actualizados
    extras = [yoga_lunes, spinning_martes, yoga_miercoles, spinning_jueves, crossfit_miercoles]  # Clases adicionales para variar
    for indice, socio in enumerate(socios[:10]):  # Recorre los 10 primeros socios
        inscripcion = InscripcionMensual(socio, mes)  # Crea la inscripción del mes
        for clase in (crossfit_viernes, extras[indice % len(extras)]):  # Reserva el crossfit + una clase extra
            inscripcion.agregar_clase(DetalleClaseReservada(clase_dao.buscar_por_id(clase.id, mes)))  # Agrega con el cupo real
        inscripcion_dao.guardar(inscripcion, valentina.rut)  # Guarda la inscripción completa
        if indice < 8:  # Los 8 primeros pagan su mensualidad
            total = valentina.cobrar_mensualidad(inscripcion)  # Cobra y extiende la membresía hasta fin de mes
            inscripcion_dao.registrar_pago(inscripcion, total, valentina.rut)  # Guarda el pago y la membresía

    # 5) Suplementos importados con precio en CLP según el dólar del día
    suplementos = [  # Productos del mesón
        Suplemento("PROT-01", "Proteina Whey 2 lb", 12, 45.00),
        Suplemento("CREA-01", "Creatina Monohidrato 300 g", 20, 25.00),
        Suplemento("PRE-01", "Pre-entreno 30 porciones", 8, 32.50),
        Suplemento("BCAA-01", "BCAA 250 g", 0, 22.00),
    ]
    valor_dolar = DolarService(conexion).obtener_valor()  # Obtiene el dólar del día (API o respaldo)
    for s in suplementos:  # Recorre los productos
        s.actualizar_precio(valor_dolar)  # Calcula el precio en pesos
        SuplementoDao(conexion).insertar(s)  # Guarda el producto
    return True  # Indica que se cargaron datos


if __name__ == "__main__":  # Solo se ejecuta si se llama directamente: python seed.py
    conexion = conectar.crear_conexion()  # Abre la conexión a powerfit.db
    if cargar_datos_demo(conexion):  # Intenta cargar los datos
        print("Datos de ejemplo cargados correctamente.")  # Mensaje de éxito
        print(f"  Instructor:    11.111.111-1 / {PASSWORD_INSTRUCTOR}")  # Credenciales del instructor
        print(f"  Recepcionista: 22.222.222-2 / {PASSWORD_RECEPCION}")  # Credenciales de la recepcionista
    else:  # Si ya había datos...
        print("La base de datos ya tenia datos: no se cargo nada.")  # ...se informa
    conexion.close()  # Cierra la conexión
