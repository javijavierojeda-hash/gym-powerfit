"""
Pruebas del modelo de dominio (sin base de datos).
Cada prueba corresponde a un requerimiento del informe.
"""

from datetime import date, time, timedelta  # Tipos de fecha y hora
import pytest  # Framework de pruebas
from model.clase import Clase  # Clase abstracta
from model.crossfit import Crossfit  # Tipos de clase
from model.spinning import Spinning
from model.yoga import Yoga
from model.cupo_lleno_exception import CupoLlenoException  # Excepciones propias
from model.membresia_vencida_exception import MembresiaVencidaException
from model.detalle_clase_reservada import DetalleClaseReservada  # Detalle de inscripción
from model.inscripcion_mensual import InscripcionMensual  # Inscripción mensual
from model.instructor import Instructor  # Trabajadores
from model.recepcionista import Recepcionista
from model.trabajador import Trabajador
from model.socio import Socio  # Socio
from model.suplemento import Suplemento  # Suplemento
from model.validaciones import calcular_dv, es_rut_valido, formatear_rut, limpiar_rut  # RUT

HOY = date.today()  # Fecha de hoy (para membresías)
MES = HOY.strftime("%Y-%m")  # Mes actual


def hash_(password="Clave1234!"):  # Atajo para crear un hash de contraseña
    return Trabajador.generar_hash(password)  # Genera el hash seguro


# ---------------- Requerimiento 3: RUT ----------------

@pytest.mark.parametrize("rut", ["12.345.678-5", "12345678-5", "123456785", "15.678.432-k", "11.111.111-1"])  # Formatos válidos
def test_rut_valido_en_varios_formatos(rut):  # Acepta RUT válidos con o sin puntos/guion y K minúscula
    assert es_rut_valido(rut)  # Debe ser válido


@pytest.mark.parametrize("rut", ["12.345.678-9", "abc", "", "1-9", "12.345.67A-5", None])  # Casos inválidos
def test_rut_invalido(rut):  # Rechaza DV incorrecto, letras, vacío, largo inválido y None
    assert not es_rut_valido(rut)  # Debe ser inválido


def test_calculo_dv_casos_especiales():  # DV "K" y "0"
    assert calcular_dv("15678432") == "K"  # Resto 10 -> K
    assert calcular_dv("17234987") == "0"  # Resto 11 -> 0


def test_formato_y_limpieza_de_rut():  # Normaliza y formatea
    assert limpiar_rut(" 12.345.678-5 ") == "12345678-5"  # Quita puntos y espacios
    assert formatear_rut("123456785") == "12.345.678-5"  # Agrega puntos y guion


def test_no_se_crea_ficha_con_rut_invalido():  # La ficha no se crea si el RUT es inválido
    with pytest.raises(ValueError):  # Debe lanzar ValueError
        Socio("12.345.678-9", "Ana")  # DV incorrecto


# ---------------- Requerimiento 1: tipos de clase ----------------

def test_clase_es_abstracta():  # No se puede crear una "Clase" genérica
    with pytest.raises(TypeError):  # Python impide instanciar clases abstractas
        Clase("lunes", time(9))  # Intento de instanciar la abstracta


def test_cada_tipo_tiene_cupo_y_duracion_distintos():  # Cada tipo define sus propios valores
    clases = [Yoga("lunes", time(9)), Spinning("martes", time(18)), Crossfit("miercoles", time(20))]  # Una de cada tipo
    assert {c.cupo_maximo for c in clases} == {20, 15, 12}  # Cupos distintos
    assert {c.duracion_min for c in clases} == {60, 45, 50}  # Duraciones distintas


def test_polimorfismo_cupos_disponibles():  # Mismo método, regla distinta según el tipo
    assert Yoga("lunes", time(9), inscritos=5).cupos_disponibles() == 15  # 20 - 5
    assert Spinning("martes", time(18), inscritos=5, bicicletas_operativas=12).cupos_disponibles() == 7  # 12 bicis - 5
    assert Crossfit("miercoles", time(20), inscritos=5).cupos_disponibles() == 5  # 12 - 2 reservados - 5


def test_bicicletas_fuera_de_rango():  # El setter valida las bicicletas
    with pytest.raises(ValueError):  # Más de 15 no es posible
        Spinning("martes", time(18), bicicletas_operativas=16)  # Valor inválido


def test_dia_invalido():  # Solo días reales
    with pytest.raises(ValueError):  # "feriado" no es un día de la semana
        Yoga("feriado", time(9))  # Día inválido


# ---------------- Requerimiento 4 y 5: inscripción y cupo ----------------

def test_inscripcion_agrupa_varias_clases_y_calcula_total():  # Una inscripción con varias clases
    socio = Socio("12.345.678-5", "Ana")  # Socia
    inscripcion = InscripcionMensual(socio, MES)  # Inscripción del mes
    inscripcion.agregar_clase(DetalleClaseReservada(Yoga("lunes", time(9))))  # Yoga los lunes
    inscripcion.agregar_clase(DetalleClaseReservada(Crossfit("miercoles", time(20))))  # Crossfit los miércoles
    assert len(inscripcion.detalles) == 2  # Dos clases bajo la misma inscripción
    assert inscripcion.calcular_total() == 15000 + 22000  # Suma de precios
    assert inscripcion.detalles[0].resumen() == "Yoga · lunes 09:00"  # Resumen del detalle


def test_cupo_lleno_lanza_excepcion_y_no_agrega():  # Requerimiento 5
    crossfit = Crossfit("viernes", time(18, 30), inscritos=10)  # Crossfit ya lleno (10 vendibles)
    inscripcion = InscripcionMensual(Socio("12.345.678-5", "Ana"), MES)  # Inscripción
    with pytest.raises(CupoLlenoException) as info:  # Debe lanzar la excepción propia
        inscripcion.agregar_clase(DetalleClaseReservada(crossfit))  # Intento de reservar
    assert info.value.clase is crossfit  # La excepción guarda la clase
    assert "cupo maximo" in str(info.value)  # Mensaje del UML
    assert inscripcion.detalles == ()  # No se agregó nada
    assert crossfit.inscritos == 10  # No se sumó un inscrito


def test_no_se_reserva_dos_veces_la_misma_clase():  # Evita duplicados
    yoga = Yoga("lunes", time(9))  # Clase
    inscripcion = InscripcionMensual(Socio("12.345.678-5", "Ana"), MES)  # Inscripción
    inscripcion.agregar_clase(DetalleClaseReservada(yoga))  # Primera reserva
    with pytest.raises(ValueError):  # La segunda debe fallar
        inscripcion.agregar_clase(DetalleClaseReservada(yoga))  # Reserva repetida


def test_lista_de_detalles_protegida():  # Encapsulamiento: no se puede alterar desde afuera
    inscripcion = InscripcionMensual(Socio("12.345.678-5", "Ana"), MES)  # Inscripción
    with pytest.raises(AttributeError):  # Una tupla no tiene append
        inscripcion.detalles.append("hack")  # Intento de modificar


def test_mes_con_formato_invalido():  # El mes debe ser AAAA-MM
    with pytest.raises(ValueError):  # Formato incorrecto
        InscripcionMensual(Socio("12.345.678-5", "Ana"), "10-2026")  # Mes al revés


# ---------------- Requerimiento 5: membresía vencida ----------------

def test_socio_nuevo_no_puede_ingresar_hasta_pagar():  # La membresía nace pendiente de pago
    socio = Socio("12.345.678-5", "Ana")  # Socia recién registrada
    with pytest.raises(MembresiaVencidaException) as info:  # No puede ingresar
        socio.puede_ingresar()  # Control de ingreso
    assert info.value.socio is socio  # La excepción guarda al socio


def test_membresia_vigente_permite_ingreso():  # Membresía al día
    socio = Socio("12.345.678-5", "Ana", HOY - timedelta(days=5), HOY + timedelta(days=10))  # Vigente
    assert socio.puede_ingresar() is True  # Puede ingresar
    assert socio.membresia.dias_restantes() == 10  # Le quedan 10 días


def test_membresia_vencida_bloquea_ingreso():  # Membresía vencida
    socio = Socio("12.345.678-5", "Ana", HOY - timedelta(days=40), HOY - timedelta(days=10))  # Venció hace 10 días
    with pytest.raises(MembresiaVencidaException) as info:  # Se niega el ingreso
        socio.puede_ingresar()  # Control de ingreso
    assert info.value.fecha_vencimiento == HOY - timedelta(days=10)  # Guarda la fecha de vencimiento


# ---------------- Requerimiento 2: trabajadores ----------------

def test_trabajador_es_abstracto():  # No existe el "trabajador genérico"
    with pytest.raises(TypeError):  # Python impide instanciarlo
        Trabajador("11.111.111-1", "X", hash_())  # Intento de instanciar la abstracta


def test_login_con_hash_seguro():  # La contraseña se guarda hasheada con salt
    h1, h2 = hash_("MiClave123"), hash_("MiClave123")  # Dos hash de la misma clave
    assert h1 != h2  # Salt distinto -> hash distinto
    assert "MiClave123" not in h1  # Nunca se guarda en texto plano
    instructor = Instructor("11.111.111-1", "Camila", h1)  # Instructora
    assert instructor.login("MiClave123")  # Clave correcta
    assert not instructor.login("otraClave")  # Clave incorrecta


def test_no_se_acepta_password_en_texto_plano():  # El constructor exige un hash
    with pytest.raises(ValueError):  # Texto plano rechazado
        Instructor("11.111.111-1", "Camila", "123456789")  # "Hash" falso


def test_password_corta_rechazada():  # Largo mínimo
    with pytest.raises(ValueError):  # Menos de 8 caracteres
        Trabajador.generar_hash("123")  # Clave débil


def test_recepcionista_no_puede_crear_ni_modificar_clases():  # Restricción estructural del requerimiento 2
    recepcionista = Recepcionista("22.222.222-2", "Vale", hash_())  # Recepcionista
    assert not hasattr(recepcionista, "crear_clase")  # No tiene método para crear clases
    assert not hasattr(recepcionista, "dictar_clase")  # Ni para dictarlas
    assert recepcionista.rol == "recepcionista"  # Su rol


def test_instructor_crea_clase_asignada_a_el():  # Solo el instructor crea clases
    instructor = Instructor("11.111.111-1", "Camila", hash_())  # Instructora
    clase = instructor.crear_clase("spinning", "martes", time(18))  # Crea una clase
    assert isinstance(clase, Spinning) and clase.instructor_rut == instructor.rut  # Tipo correcto y asignada a ella


def test_marcar_asistencia_valida_instructor_y_membresia():  # Reglas de marcar_asistencia
    camila = Instructor("11.111.111-1", "Camila", hash_())  # Instructora dueña
    otro = Instructor("17.654.321-3", "Diego", hash_())  # Otro instructor
    clase = camila.crear_clase("yoga", "lunes", time(9))  # Clase de Camila
    vigente = Socio("12.345.678-5", "Ana", HOY, HOY + timedelta(days=5))  # Socia al día
    vencido = Socio("15.678.432-K", "Pedro")  # Socio sin pagar
    camila.marcar_asistencia(clase, vigente)  # No lanza nada: se puede marcar
    with pytest.raises(PermissionError):  # Otro instructor no puede
        otro.marcar_asistencia(clase, vigente)  # Intento de otro instructor
    with pytest.raises(MembresiaVencidaException):  # Socio vencido no puede
        camila.marcar_asistencia(clase, vencido)  # Intento con membresía vencida


def test_cobrar_mensualidad_renueva_membresia_y_evita_doble_cobro():  # Cobro de mensualidad
    recepcionista = Recepcionista("22.222.222-2", "Vale", hash_())  # Recepcionista
    socio = Socio("12.345.678-5", "Ana")  # Socia pendiente de pago
    inscripcion = InscripcionMensual(socio, MES)  # Inscripción del mes
    inscripcion.agregar_clase(DetalleClaseReservada(Yoga("lunes", time(9))))  # Reserva Yoga
    assert recepcionista.cobrar_mensualidad(inscripcion) == 15000  # Cobra el total
    assert inscripcion.pagada and socio.puede_ingresar()  # Queda pagada y puede ingresar
    with pytest.raises(ValueError):  # Segundo cobro rechazado
        recepcionista.cobrar_mensualidad(inscripcion)  # Doble cobro


def test_no_se_cobra_inscripcion_vacia():  # Regla 1..* del UML
    recepcionista = Recepcionista("22.222.222-2", "Vale", hash_())  # Recepcionista
    with pytest.raises(ValueError):  # Sin clases no se cobra
        recepcionista.cobrar_mensualidad(InscripcionMensual(Socio("12.345.678-5", "Ana"), MES))  # Inscripción vacía


# ---------------- Requerimiento 6: suplementos ----------------

def test_precio_suplemento_segun_dolar():  # precio_clp = precio_usd * dólar
    whey = Suplemento("prot-01", "Whey", 10, 45.0)  # Suplemento de USD 45
    whey.actualizar_precio(950.5)  # Dólar del día
    assert whey.precio_clp == round(45 * 950.5)  # Precio en pesos
    assert whey.codigo == "PROT-01"  # Código normalizado


@pytest.mark.parametrize("dolar", [0, -1, "950"])  # Valores inválidos del dólar
def test_dolar_invalido(dolar):  # Protege contra datos erróneos
    with pytest.raises(ValueError):  # Debe rechazarse
        Suplemento("A", "B", 1, 10).actualizar_precio(dolar)  # Intento con valor inválido


def test_venta_descuenta_stock_y_valida():  # Venta en mesón
    whey = Suplemento("PROT-01", "Whey", 3, 45.0)  # 3 unidades
    with pytest.raises(ValueError):  # Sin precio en CLP no se vende
        whey.vender(1)  # Intento sin cotizar
    whey.actualizar_precio(1000)  # Cotiza con dólar a $1.000
    assert whey.vender(2) == 90000 and whey.stock == 1  # Vende 2 y queda 1
    with pytest.raises(ValueError):  # No hay stock suficiente
        whey.vender(5)  # Intento de vender de más
