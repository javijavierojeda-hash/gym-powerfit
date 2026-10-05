"""
Script de demostración del modelo de clases de PowerFit (Evaluación Sumativa N°2).

Crea objetos del negocio y muestra en pantalla los 4 requisitos:
  1. Los tres subtipos (Yoga, Spinning, Crossfit) con su método distinto.
  2. El dato con validación en el setter (RUT del socio).
  3. La transacción (InscripcionMensual) con sus líneas de detalle.
  4. Las dos reglas del negocio, provocadas a propósito y capturadas con try/except.

Solo usa la librería estándar de Python (no necesita instalar nada, ni internet,
ni base de datos).  Uso:  python main.py
"""

from __future__ import annotations  # Permite usar anotaciones modernas también en Python 3.7 a 3.9

from datetime import date, time, timedelta  # Tipos de fecha, hora y diferencia de tiempo
from model.trabajador import Trabajador  # Clase base abstracta de los trabajadores
from model.instructor import Instructor  # Subtipo de Trabajador
from model.recepcionista import Recepcionista  # Subtipo de Trabajador
from model.yoga import Yoga  # Subtipo de Clase
from model.spinning import Spinning  # Subtipo de Clase
from model.crossfit import Crossfit  # Subtipo de Clase
from model.socio import Socio  # Socio (se compone de una Membresia)
from model.inscripcion_mensual import InscripcionMensual  # La transacción del negocio
from model.suplemento import Suplemento  # Producto importado cotizado en dólares
from model.cupo_lleno_exception import CupoLlenoException  # Excepción propia: regla 1
from model.membresia_vencida_exception import MembresiaVencidaException  # Excepción propia: regla 2

VALOR_DOLAR_DEMO = 950.0  # Dólar fijo para la demo (así main.py no depende de internet)


def titulo(texto: str) -> None:  # Imprime un título de sección
    print("\n" + "=" * 70)  # Línea superior
    print(" " + texto)  # Texto del título
    print("=" * 70)  # Línea inferior


def pesos(monto: int) -> str:  # Formatea un monto en pesos chilenos
    return "$" + f"{monto:,}".replace(",", ".")  # Ej: 15000 -> "$15.000"


def main() -> None:  # Función principal de la demostración
    print("POWERFIT - Demostración del modelo de clases (Evaluación Sumativa N°2)")  # Encabezado

    # ---------- Objetos base del negocio ----------
    camila = Instructor("11.111.111-1", "Camila Rojas", Trabajador.generar_hash("Instructor123!"))  # Instructora
    valentina = Recepcionista("22.222.222-2", "Valentina Soto", Trabajador.generar_hash("Recepcion123!"))  # Recepcionista
    print(f"Trabajadores: {camila} | {valentina}")  # Muestra los dos subtipos de Trabajador

    # =====================================================================
    titulo("REQUISITO 1 - Tres subtipos con su método distinto (polimorfismo)")
    print("Método abstracto: Clase.cupos_disponibles()  ->  sobrescrito en model/yoga.py,")  # Indica dónde está en el código
    print("model/spinning.py y model/crossfit.py. Cada subtipo llama a super().__init__().\n")  # Indica el uso de super()
    yoga = camila.crear_clase("yoga", "lunes", time(9, 0))  # Crea un Yoga (subtipo de Clase)
    spinning = camila.crear_clase("spinning", "martes", time(18, 0))  # Crea un Spinning (subtipo de Clase)
    spinning.bicicletas_operativas = 13  # Dos bicicletas en mantención: su regla las descuenta
    crossfit = camila.crear_clase("crossfit", "miercoles", time(20, 0))  # Crea un Crossfit (subtipo de Clase)
    clases = [yoga, spinning, crossfit]  # Lista con los tres subtipos mezclados
    for clase in clases:  # Recorre la lista SIN preguntar el tipo de cada objeto...
        disponibles = clase.cupos_disponibles()  # ...y cada uno responde con SU propia regla (polimorfismo)
        print(f"  {clase.tipo:<9} cupo máximo {clase.cupo_maximo:>2} | {clase.duracion_min} min | "
              f"cupos_disponibles() = {disponibles}")  # Muestra el resultado distinto de cada subtipo
    print("\n  Regla de cada subtipo:")  # Explica por qué los resultados son distintos
    print("  - Yoga:     cupo máximo - inscritos")  # Regla de Yoga
    print("  - Spinning: bicicletas operativas (13) - inscritos")  # Regla de Spinning
    print("  - Crossfit: cupo máximo - 2 cupos reservados - inscritos")  # Regla de Crossfit

    # =====================================================================
    titulo("REQUISITO 2 - Dato con validación en el setter: Socio.rut")
    print("Setter: @rut.setter en model/socio.py (valida con el algoritmo módulo 11).\n")  # Indica dónde está
    ana = valentina.inscribir_socio("12.345.678-5", "Ana Perez")  # Crea una socia con RUT válido (pasa por el setter)
    print(f"  RUT válido   '12.345.678-5' -> ficha creada: {ana}")  # La ficha se creó
    try:  # Intenta crear un socio con RUT inválido
        Socio("12.345.678-9", "Pedro Falso")  # El constructor usa el setter, que valida el RUT
    except ValueError as error:  # El setter rechaza el RUT
        print(f"  RUT inválido '12.345.678-9' -> ficha NO creada (ValueError: {error})")  # Informa el error y sigue
    try:  # Intenta CAMBIAR el RUT de un socio ya creado por uno inválido
        ana.rut = "abc"  # Asignación directa: también pasa por el setter
    except ValueError as error:  # El setter rechaza el cambio
        print(f"  Cambio a 'abc' rechazado (ValueError: {error}); RUT se mantiene: {ana.rut_formateado}")  # El dato no cambió

    # =====================================================================
    titulo("REQUISITO 3 - Transacción con sus líneas de detalle: InscripcionMensual")
    print("InscripcionMensual.agregar_clase(clase) CREA cada DetalleClaseReservada dentro")  # Explica la composición
    print("de la inscripción (composición) y recibe la Clase que ya existe (agregación).\n")  # Explica la agregación
    mes = date.today().strftime("%Y-%m")  # Mes actual en formato AAAA-MM
    inscripcion = InscripcionMensual(ana, mes)  # AGREGACIÓN: recibe a la socia que ya existe
    inscripcion.agregar_clase(yoga)  # Reserva Yoga los lunes
    inscripcion.agregar_clase(crossfit)  # Reserva Crossfit los miércoles
    print(f"  {inscripcion}")  # Resumen de la inscripción
    for numero, detalle in enumerate(inscripcion.detalles, start=1):  # Recorre las líneas de detalle
        print(f"   Línea {numero}: {detalle.resumen():<28} {pesos(detalle.subtotal):>8}")  # Muestra cada línea y su precio
    print(f"   {'TOTAL calcular_total()':<36} {pesos(inscripcion.calcular_total()):>8}")  # Total de la transacción
    total = valentina.cobrar_mensualidad(inscripcion)  # La recepcionista cobra y se renueva la membresía
    print(f"  Recepcionista.cobrar_mensualidad() -> cobrado {pesos(total)}; {ana.membresia}")  # Muestra el cobro

    # =====================================================================
    titulo("REQUISITO 4 - Las dos reglas del negocio (excepciones propias)")
    print("Regla 1: no inscribir en una clase con el cupo lleno.")  # Primera regla
    print("  Lanzada por: InscripcionMensual.agregar_clase()  (model/inscripcion_mensual.py)")  # Dónde se lanza
    crossfit.inscritos = 10  # Simula que el Crossfit ya llegó a su cupo vendible (12 - 2 reservados)
    pedro = valentina.inscribir_socio("15.678.432-K", "Pedro Gonzalez")  # Otro socio
    otra_inscripcion = InscripcionMensual(pedro, mes)  # Su inscripción del mes
    try:  # Provoca la regla 1 a propósito
        otra_inscripcion.agregar_clase(crossfit)  # Intenta reservar una clase llena
    except CupoLlenoException as error:  # Captura la excepción propia del dominio
        print(f"  -> CupoLlenoException capturada: {error}")  # Informa el error...
        print(f"     La inscripción quedó sin cambios: {len(otra_inscripcion.detalles)} clases reservadas.")  # ...y sigue

    print("\nRegla 2: no dejar entrar a un socio con la membresía vencida.")  # Segunda regla
    print("  Lanzada por: Socio.puede_ingresar()  (model/socio.py)")  # Dónde se lanza
    agustin = Socio("19.283.746-4", "Agustin Reyes",  # Socio cuya membresía venció hace 30 días
                    date.today() - timedelta(days=60), date.today() - timedelta(days=30))
    for socio in (ana, agustin):  # Revisa el ingreso de una socia al día y de un socio vencido
        try:  # Provoca la regla 2 a propósito con el socio vencido
            socio.puede_ingresar()  # Lanza MembresiaVencidaException si no está vigente
            print(f"  -> {socio.nombre}: puede ingresar ({socio.membresia})")  # Socia al día
        except MembresiaVencidaException as error:  # Captura la excepción propia del dominio
            print(f"  -> MembresiaVencidaException capturada: {error}")  # Informa el error y sigue

    # =====================================================================
    titulo("EXTRA - Suplemento cotizado con el dólar del día")
    whey = Suplemento("PROT-01", "Proteina Whey 2 lb", 10, 45.00)  # Producto de USD 45
    whey.actualizar_precio(VALOR_DOLAR_DEMO)  # Calcula el precio en pesos
    print(f"  {whey} x dólar {VALOR_DOLAR_DEMO:.0f} = {pesos(whey.precio_clp)} CLP")  # Muestra el cálculo
    print(f"  Venta de 2 unidades: {pesos(valentina.vender_suplemento(whey, 2))} (stock restante: {whey.stock})")  # Vende

    print("\nDemostración finalizada sin errores no controlados.")  # Mensaje final


if __name__ == "__main__":  # Verifica si el script se está ejecutando directamente
    main()  # Llama a la función principal
