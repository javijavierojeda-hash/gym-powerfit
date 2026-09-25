"""
Pruebas de la capa de datos (DAO) con una BD en memoria.
"""

import sqlite3  # Para reconocer errores de integridad
from datetime import date, time  # Tipos de fecha y hora
import pytest  # Framework de pruebas
from dao.clase_dao import ClaseDao  # DAOs a probar
from dao.crossfit_dao import CrossfitDao
from dao.esquema import crear_esquema
from dao.instructor_dao import InstructorDao
from dao.recepcionista_dao import RecepcionistaDao
from dao.socio_dao import SocioDao
from dao.spinning_dao import SpinningDao
from dao.suplemento_dao import SuplementoDao
from dao.inscripcion_mensual_dao import InscripcionMensualDao
from dao.yoga_dao import YogaDao
from model.cupo_lleno_exception import CupoLlenoException  # Excepción de cupo lleno
from model.detalle_clase_reservada import DetalleClaseReservada  # Modelo
from model.inscripcion_mensual import InscripcionMensual
from model.instructor import Instructor
from model.recepcionista import Recepcionista
from model.socio import Socio
from model.suplemento import Suplemento
from model.trabajador import Trabajador
from model.validaciones import calcular_dv
from services.dolar_service import DolarService, VALOR_POR_DEFECTO  # Servicio del dólar

MES = date.today().strftime("%Y-%m")  # Mes actual


def rut(n: int) -> str:  # Arma un RUT válido desde un número
    return f"{n}-{calcular_dv(str(n))}"  # Número + dígito verificador


@pytest.fixture
def instructor(conexion):  # Instructora guardada en la BD
    i = Instructor("11.111.111-1", "Camila", Trabajador.generar_hash("Clave1234!"))  # Crea el objeto
    InstructorDao(conexion).insertar(i)  # Lo guarda
    return i  # Lo entrega a la prueba


def test_esquema_crea_las_15_tablas(conexion):  # El esquema completo existe
    tablas = crear_esquema(conexion)  # Es idempotente: se puede volver a ejecutar
    assert len(tablas) == 15  # 15 tablas del negocio
    assert {"trabajadores", "instructores", "clases", "yoga", "membresias", "detalles_clase_reservada"} <= set(tablas)  # Algunas clave


def test_herencia_tabla_por_tipo_trabajadores(conexion, instructor):  # Cada DAO solo ve su tipo
    assert InstructorDao(conexion).buscar_por_rut(instructor.rut).login("Clave1234!")  # Se lee como Instructor y conserva el hash
    assert RecepcionistaDao(conexion).buscar_por_rut(instructor.rut) is None  # No es recepcionista


def test_clases_se_reconstruyen_con_su_tipo(conexion, instructor):  # LEFT JOIN a las tablas hijas
    YogaDao(conexion).insertar(instructor.crear_clase("yoga", "lunes", time(9)))  # Guarda Yoga
    s = instructor.crear_clase("spinning", "martes", time(18))  # Crea Spinning
    s.bicicletas_operativas = 11  # Con 11 bicicletas
    SpinningDao(conexion).insertar(s)  # Lo guarda
    clases = ClaseDao(conexion).listar(MES)  # Lee todas
    assert [c.tipo for c in clases] == ["Yoga", "Spinning"]  # Tipos correctos y ordenados por día
    assert clases[1].bicicletas_operativas == 11  # Dato propio de la tabla hija


def test_socio_con_membresia_en_una_transaccion(conexion):  # Composición Socio-Membresia
    SocioDao(conexion).insertar(Socio("12.345.678-5", "Ana"))  # Guarda socio + membresía
    socio = SocioDao(conexion).buscar_por_rut("12.345.678-5")  # Lo busca con puntos (se normaliza)
    assert socio.nombre == "Ana" and not socio.membresia.esta_vigente()  # Reconstruido con su membresía pendiente
    with pytest.raises(sqlite3.IntegrityError):  # RUT repetido
        SocioDao(conexion).insertar(Socio("12345678-5", "Otra"))  # PK duplicada
    assert conexion.execute("SELECT COUNT(*) FROM membresias").fetchone()[0] == 1  # El rollback no dejó membresías huérfanas


def test_borrar_socio_borra_su_membresia(conexion):  # ON DELETE CASCADE
    SocioDao(conexion).insertar(Socio("12.345.678-5", "Ana"))  # Guarda socio
    conexion.execute("DELETE FROM socios")  # Borra el socio
    assert conexion.execute("SELECT COUNT(*) FROM membresias").fetchone()[0] == 0  # La membresía desapareció con él


def test_guardar_inscripcion_revisa_cupo_contra_la_bd(conexion, instructor):  # Cupo protegido en la BD
    crossfit = instructor.crear_clase("crossfit", "viernes", time(18, 30))  # Crossfit: 10 cupos vendibles
    CrossfitDao(conexion).insertar(crossfit)  # Lo guarda
    dao = InscripcionMensualDao(conexion)  # DAO de inscripciones
    for n in range(10):  # Llena la clase con 10 socios
        socio = Socio(rut(10_000_000 + n), f"Socio {n}")  # Socio nuevo
        SocioDao(conexion).insertar(socio)  # Lo guarda
        i = InscripcionMensual(socio, MES)  # Inscripción
        i.agregar_clase(DetalleClaseReservada(ClaseDao(conexion).buscar_por_id(crossfit.id, MES)))  # Reserva con el cupo real
        dao.guardar(i)  # Guarda
    # Objeto "desactualizado": en memoria cree que la clase tiene 0 inscritos
    socio = Socio(rut(20_000_000), "Tarde")  # Socio que llega tarde
    SocioDao(conexion).insertar(socio)  # Lo guarda
    i = InscripcionMensual(socio, MES)  # Inscripción
    i.agregar_clase(DetalleClaseReservada(crossfit))  # En memoria "hay cupo" (dato viejo)
    with pytest.raises(CupoLlenoException):  # Pero la BD sabe que está llena
        dao.guardar(i)  # Debe rechazarse
    assert dao.buscar(socio.rut, MES) is None  # Rollback: no quedó nada guardado


def test_una_inscripcion_por_socio_y_mes(conexion, instructor):  # UNIQUE(socio, mes)
    yoga = instructor.crear_clase("yoga", "lunes", time(9))  # Clase
    YogaDao(conexion).insertar(yoga)  # La guarda
    socio = Socio("12.345.678-5", "Ana")  # Socia
    SocioDao(conexion).insertar(socio)  # La guarda
    for intento in range(2):  # Dos intentos para el mismo mes
        i = InscripcionMensual(socio, MES)  # Inscripción
        i.agregar_clase(DetalleClaseReservada(ClaseDao(conexion).buscar_por_id(yoga.id, MES)))  # Reserva
        if intento == 0:  # La primera funciona
            InscripcionMensualDao(conexion).guardar(i)  # Se guarda
        else:  # La segunda...
            with pytest.raises(ValueError):  # ...se rechaza
                InscripcionMensualDao(conexion).guardar(i)  # Duplicado


def test_pago_se_registra_una_sola_vez(conexion, instructor):  # Sin doble cobro en la BD
    yoga = instructor.crear_clase("yoga", "lunes", time(9))  # Clase
    YogaDao(conexion).insertar(yoga)  # La guarda
    recepcionista = Recepcionista("22.222.222-2", "Vale", Trabajador.generar_hash("Clave1234!"))  # Recepcionista
    RecepcionistaDao(conexion).insertar(recepcionista)  # La guarda
    socio = Socio("12.345.678-5", "Ana")  # Socia
    SocioDao(conexion).insertar(socio)  # La guarda
    i = InscripcionMensual(socio, MES)  # Inscripción
    i.agregar_clase(DetalleClaseReservada(yoga))  # Reserva Yoga
    dao = InscripcionMensualDao(conexion)  # DAO
    dao.guardar(i, recepcionista.rut)  # Guarda
    total = recepcionista.cobrar_mensualidad(i)  # Cobra en el modelo
    dao.registrar_pago(i, total, recepcionista.rut)  # Registra el pago
    assert SocioDao(conexion).buscar_por_rut(socio.rut).membresia.esta_vigente()  # La membresía quedó renovada en la BD
    with pytest.raises(ValueError):  # Un segundo registro de pago...
        dao.registrar_pago(i, total, recepcionista.rut)  # ...se rechaza


def test_venta_no_deja_stock_negativo(conexion):  # UPDATE ... WHERE stock >= ?
    s = Suplemento("PROT-01", "Whey", 2, 45.0)  # 2 unidades
    s.actualizar_precio(1000)  # Cotiza
    dao = SuplementoDao(conexion)  # DAO
    dao.insertar(s)  # Guarda
    dao.registrar_venta(s, 2, 90000, 1000)  # Vende las 2
    with pytest.raises(ValueError):  # No queda stock
        dao.registrar_venta(s, 1, 45000, 1000)  # Intento de vender otra
    assert dao.buscar("PROT-01").stock == 0 and len(dao.listar_ventas()) == 1  # Stock 0 y una sola venta registrada


def test_dolar_usa_api_valida_y_luego_respaldo(conexion):  # Servicio del dólar
    servicio = DolarService(conexion, obtener_json=lambda: {"serie": [{"fecha": "2026-09-25T03:00:00.000Z", "valor": 931.5}]})  # API simulada
    cotizacion = servicio.obtener_cotizacion()  # Consulta
    assert (cotizacion.valor, cotizacion.fuente) == (931.5, "api")  # Valor real desde la "API"
    DolarService.limpiar_cache()  # Borra la caché para forzar otra consulta
    caida = DolarService(conexion)  # Sin función: usa la API real, que en las pruebas está "caída"
    assert (caida.obtener_valor(), caida.obtener_cotizacion().fuente) == (931.5, "respaldo")  # Usa el último valor guardado


@pytest.mark.parametrize("valor", ["950", -5, 99999, True])  # Respuestas inválidas de la API
def test_dolar_rechaza_datos_invalidos_de_la_api(valor):  # No se confía en datos externos
    servicio = DolarService(None, obtener_json=lambda: {"serie": [{"valor": valor}]})  # API con dato malo
    assert servicio.obtener_cotizacion().valor == VALOR_POR_DEFECTO  # Se descarta y usa el valor por defecto
