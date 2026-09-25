"""
Demostración por consola de PowerFit (estilo del main.py del profesor).

1. Crea las tablas en la base de datos y muestra cuáles existen.
2. Demuestra en memoria las reglas de negocio de los 6 requerimientos.

Uso:  python main.py
"""

from datetime import date, time, timedelta  # Tipos de fecha, hora y diferencia de tiempo
import conectar  # Módulo de conexión a la base de datos
from dao.esquema import crear_esquema  # Función que crea todas las tablas
from model.trabajador import Trabajador  # Para generar hash de contraseña
from model.instructor import Instructor  # Clase Instructor
from model.recepcionista import Recepcionista  # Clase Recepcionista
from model.inscripcion_mensual import InscripcionMensual  # Clase InscripcionMensual
from model.detalle_clase_reservada import DetalleClaseReservada  # Clase DetalleClaseReservada
from model.suplemento import Suplemento  # Clase Suplemento
from model.socio import Socio  # Clase Socio
from model.cupo_lleno_exception import CupoLlenoException  # Excepción de cupo lleno
from model.membresia_vencida_exception import MembresiaVencidaException  # Excepción de membresía vencida
from services.dolar_service import DolarService  # Servicio del dólar


def titulo(texto: str) -> None:  # Imprime un título de sección
    print(f"\n{'=' * 60}\n {texto}\n{'=' * 60}")  # Línea, texto y línea


def main():  # Función principal de ejecución
    # ---------- 1. Base de datos ----------
    titulo("1. Inicializando Base de Datos")  # Título de la sección
    conn = conectar.crear_conexion()  # Llama a crear_conexion para obtener el objeto de conexión
    for tabla in crear_esquema(conn):  # Crea las tablas y recorre sus nombres
        print(f"- {tabla}")  # Imprime el nombre de cada tabla del negocio

    # ---------- 2. Trabajadores y permisos ----------
    titulo("2. Trabajadores (herencia + login seguro)")  # Título de la sección
    camila = Instructor("11.111.111-1", "Camila Rojas", Trabajador.generar_hash("Instructor123!"))  # Crea una instructora
    valentina = Recepcionista("22.222.222-2", "Valentina Soto", Trabajador.generar_hash("Recepcion123!"))  # Crea una recepcionista
    print(camila, "-> login correcto:", camila.login("Instructor123!"))  # Prueba el login con la clave correcta
    print(camila, "-> login con clave erronea:", camila.login("hola1234"))  # Prueba el login con una clave incorrecta
    print("La recepcionista puede crear clases?", hasattr(valentina, "crear_clase"))  # La recepcionista no tiene ese método

    # ---------- 3. Polimorfismo en las clases ----------
    titulo("3. Tipos de clase (polimorfismo en cupos_disponibles)")  # Título de la sección
    yoga = camila.crear_clase("yoga", "lunes", time(9, 0))  # Crea una clase de Yoga
    spinning = camila.crear_clase("spinning", "martes", time(18, 0))  # Crea una clase de Spinning
    spinning.bicicletas_operativas = 13  # Dos bicicletas en mantención
    crossfit = camila.crear_clase("crossfit", "miercoles", time(20, 0))  # Crea una clase de Crossfit
    for clase in (yoga, spinning, crossfit):  # Recorre las tres clases con el MISMO código...
        print(f"{clase.tipo:9} cupo {clase.cupo_maximo:2}, {clase.duracion_min} min -> "  # ...mostrando sus datos...
              f"disponibles: {clase.cupos_disponibles()}")  # ...y cada una calcula distinto sus cupos

    # ---------- 4. Validación de RUT ----------
    titulo("4. Validacion de RUT antes de crear la ficha")  # Título de la sección
    for rut in ("12.345.678-5", "12.345.678-9", "abc"):  # Prueba un RUT válido y dos inválidos
        try:  # Intenta crear el socio
            socio = valentina.inscribir_socio(rut, "Socio de prueba")  # La recepcionista inscribe al socio
            print(f"{rut:14} -> ficha creada: {socio}")  # Si el RUT es válido, se crea la ficha
        except ValueError as error:  # Si el RUT es inválido...
            print(f"{rut:14} -> RECHAZADO: {error}")  # ...no se crea la ficha

    # ---------- 5. Inscripción mensual y cupo lleno ----------
    titulo("5. Inscripcion mensual con varias clases + cupo lleno")  # Título de la sección
    ana = valentina.inscribir_socio("12.345.678-5", "Ana Perez")  # Crea la socia Ana
    mes = date.today().strftime("%Y-%m")  # Mes actual
    inscripcion = InscripcionMensual(ana, mes)  # Crea la inscripción del mes
    inscripcion.agregar_clase(DetalleClaseReservada(yoga))  # Reserva Yoga el lunes
    inscripcion.agregar_clase(DetalleClaseReservada(crossfit))  # Reserva Crossfit el miércoles
    for detalle in inscripcion.detalles:  # Recorre el detalle de la inscripción
        print(f"  - {detalle.resumen():30} ${detalle.subtotal:,}".replace(",", "."))  # Muestra cada clase y su precio
    print(f"  TOTAL: ${inscripcion.calcular_total():,}".replace(",", "."))  # Muestra el total del mes
    crossfit.inscritos = 10  # Simula que el Crossfit ya llegó a su máximo vendible (12 - 2 reservados)
    pedro = Socio("15.678.432-K", "Pedro Gonzalez")  # Otro socio
    try:  # Intenta inscribir a Pedro en la clase llena
        InscripcionMensual(pedro, mes).agregar_clase(DetalleClaseReservada(crossfit))  # Agrega Crossfit
    except CupoLlenoException as error:  # La excepción propia detiene la operación
        print("  CupoLlenoException ->", error)  # Muestra el mensaje

    # ---------- 6. Cobro y control de ingreso ----------
    titulo("6. Cobro de mensualidad y control de ingreso")  # Título de la sección
    try:  # Ana intenta entrar ANTES de pagar
        ana.puede_ingresar()  # Revisa la membresía
    except MembresiaVencidaException as error:  # Si no está vigente...
        print("  Antes de pagar:", error)  # ...se le niega el ingreso
    total = valentina.cobrar_mensualidad(inscripcion)  # La recepcionista cobra la mensualidad
    print(f"  Cobrado ${total:,}".replace(",", "."), "->", ana.membresia)  # Muestra el cobro y la membresía renovada
    print("  Despues de pagar, puede ingresar?", ana.puede_ingresar())  # Ahora sí puede ingresar
    vencido = Socio("19.283.746-4", "Agustin Reyes", date.today() - timedelta(days=60), date.today() - timedelta(days=30))  # Socio vencido
    try:  # Intenta ingresar con la membresía vencida
        vencido.puede_ingresar()  # Revisa la membresía
    except MembresiaVencidaException as error:  # Se lanza la excepción propia
        print("  MembresiaVencidaException ->", error)  # Muestra el mensaje

    # ---------- 7. Suplementos con dólar del día ----------
    titulo("7. Suplementos cotizados con el dolar del dia")  # Título de la sección
    cotizacion = DolarService(conn).obtener_cotizacion()  # Obtiene el dólar (API, respaldo o valor por defecto)
    print(f"  Dolar: ${cotizacion.valor:,.2f} (fuente: {cotizacion.fuente})")  # Muestra el valor y su origen
    whey = Suplemento("PROT-01", "Proteina Whey 2 lb", 10, 45.00)  # Crea un suplemento de USD 45
    whey.actualizar_precio(cotizacion.valor)  # Calcula su precio en pesos
    print(f"  {whey} -> ${whey.precio_clp:,} CLP".replace(",", "."))  # Muestra el precio en CLP
    print(f"  Venta de 2 unidades: ${valentina.vender_suplemento(whey, 2):,}".replace(",", "."), f"(stock restante: {whey.stock})")  # Vende 2

    conn.close()  # Cierra la conexión a la base de datos
    print("\nProceso finalizado exitosamente.")  # Mensaje final de éxito


if __name__ == "__main__":  # Verifica si el script se está ejecutando directamente
    main()  # Llama a la función principal
