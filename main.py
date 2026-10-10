"""
PowerFit - Programa principal por consola (Evaluación Sumativa N°3).

Sistema de gestión del gimnasio PowerFit con menú interactivo:
- Persistencia en SQLite mediante DAO (carpeta dao/), con CRUD de socios,
  clases e inscripciones mensuales (la transacción con su detalle).
- Validación de TODAS las entradas antes de usarlas (consola/entradas.py y
  los setters del modelo): un dato inválido se rechaza con un mensaje y el
  programa sigue funcionando.
- Precio de los suplementos con el dólar del día obtenido desde la API
  mindicador.cl con la librería requests (services/dolar_service.py).
- Inicio de sesión con RUT y contraseña (hash PBKDF2); cada rol ve solo sus
  opciones (la recepcionista no crea clases, el instructor no cobra).

Uso:  python main.py      (las tablas y los datos de ejemplo se crean solos)
"""

from __future__ import annotations  # Permite usar anotaciones modernas (str | None) también en Python 3.7 a 3.9

import hashlib  # Para gastar el mismo tiempo cuando el RUT no existe (login)
import sqlite3  # Para reconocer los errores de integridad de la base de datos
from datetime import date, timedelta  # Fechas de membresía y meses de inscripción

import conectar  # Conexión a la base de datos SQLite
from consola.entradas import (  # Lectura segura de datos por teclado
    OperacionCancelada, error, leer, pedir_clave, pedir_entero, pedir_fecha, pedir_hora,
    pedir_opcion, pedir_rut, pedir_si_no, pedir_texto,
)
from dao.asistencia_dao import AsistenciaDao  # DAO de asistencias
from dao.clase_dao import ClaseDao  # DAO genérico de clases (lectura, horario y eliminación)
from dao.crossfit_dao import CrossfitDao  # DAO de Crossfit
from dao.esquema import crear_esquema  # Crea todas las tablas si no existen
from dao.inscripcion_mensual_dao import InscripcionMensualDao  # DAO de la transacción y su detalle
from dao.instructor_dao import InstructorDao  # DAO de instructores
from dao.recepcionista_dao import RecepcionistaDao  # DAO de recepcionistas
from dao.socio_dao import SocioDao  # DAO de socios
from dao.spinning_dao import SpinningDao  # DAO de Spinning
from dao.suplemento_dao import SuplementoDao  # DAO de suplementos
from dao.yoga_dao import YogaDao  # DAO de Yoga
from model.clase import DIAS_SEMANA  # Días válidos para programar clases
from model.cupo_lleno_exception import CupoLlenoException  # Regla 1 del negocio
from model.inscripcion_mensual import InscripcionMensual  # La transacción del negocio
from model.membresia_vencida_exception import MembresiaVencidaException  # Regla 2 del negocio
from model.socio import Socio  # Socio del gimnasio
from model.spinning import Spinning  # Para el rango de bicicletas operativas
from seed import cargar_datos_demo  # Datos de ejemplo para una base de datos nueva
from services.dolar_service import DolarService  # Dólar del día (API mindicador.cl con requests)

MAX_INTENTOS_LOGIN = 5  # Tras 5 intentos fallidos el programa se cierra (protección contra fuerza bruta)
DAO_POR_TIPO = {"yoga": YogaDao, "spinning": SpinningDao, "crossfit": CrossfitDao}  # Qué DAO guarda cada tipo de clase


# =====================================================================
# Utilidades de presentación
# =====================================================================

def titulo(texto: str) -> None:  # Imprime el título de una sección
    print("\n" + "=" * 64)  # Línea superior
    print(f" {texto}")  # Texto del título
    print("=" * 64)  # Línea inferior


def pesos(monto: float) -> str:  # Formatea un monto en pesos chilenos
    return "$" + f"{round(monto):,}".replace(",", ".")  # Ej: 15000 -> "$15.000"


def dolar(valor: float) -> str:  # Formatea el valor del dólar con 2 decimales al estilo chileno
    return "$" + f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")  # Ej: 940.5 -> "$940,50"


def mes_actual() -> str:  # Mes actual en formato AAAA-MM
    return date.today().strftime("%Y-%m")  # Ej: "2026-10"


def mes_siguiente() -> str:  # Mes siguiente en formato AAAA-MM
    hoy = date.today()  # Fecha actual
    return (date(hoy.year, hoy.month, 28) + timedelta(days=4)).strftime("%Y-%m")  # Del día 28 + 4 días siempre cae en el mes siguiente


def estado_membresia(socio: Socio) -> str:  # Describe la membresía del socio en palabras
    m = socio.membresia  # Membresía del socio (composición)
    if m.esta_vigente():  # Si está vigente...
        return f"Vigente hasta {m.fecha_vencimiento:%d-%m-%Y}"  # ...muestra hasta cuándo
    if m.fecha_vencimiento < m.fecha_inicio:  # Si nunca se ha pagado (vencimiento antes del inicio)...
        return "Pendiente de pago"  # ...está pendiente
    return f"VENCIDA el {m.fecha_vencimiento:%d-%m-%Y}"  # Si no, venció en esa fecha


def buscar_socio(conexion) -> Socio | None:  # Pide un RUT y busca al socio
    rut = pedir_rut("RUT del socio (sin puntos, ej: 12345678-5; 0 = cancelar): ")  # RUT validado (módulo 11)
    socio = SocioDao(conexion).buscar_por_rut(rut)  # Busca en la base de datos (consulta parametrizada)
    if socio is None:  # Si no existe...
        error("No existe un socio con ese RUT.")  # ...lo informa
    return socio  # Retorna el socio o None


def pedir_con_setter(mensaje: str, aplicar, obligatorio: bool = True) -> None:  # Pide un dato y lo valida en el SETTER del modelo
    """
    Pide un texto y se lo entrega a 'aplicar', que lo asigna a un atributo
    del modelo. Si el setter lo rechaza (ValueError), se muestra el motivo
    y se vuelve a preguntar.
    """
    while True:  # Repite hasta que el setter acepte el dato
        texto = pedir_texto(mensaje, obligatorio=obligatorio, largo_max=100)  # Lee el texto (largo máximo)
        try:  # El setter decide si el dato es válido
            aplicar(texto)  # Asigna el dato (ej: socio.correo = texto)
            return  # Dato aceptado
        except ValueError as e:  # El setter lo rechazó
            error(str(e))  # Muestra el motivo y vuelve a preguntar


def elegir_clase(clases: list, mensaje: str = "N° de la clase (0 = cancelar): "):  # Elige una clase de una lista por su N°
    ids = {c.id: c for c in clases}  # Diccionario id -> clase
    while True:  # Repite hasta elegir un N° que exista
        numero = pedir_entero(mensaje, 1, 999999)  # Número entero positivo
        if numero in ids:  # Si es una de las clases mostradas...
            return ids[numero]  # ...la retorna
        error("Ese N° no esta en la lista.")  # Informa y vuelve a preguntar


def mostrar_clases(clases: list, instructores: dict) -> None:  # Tabla de clases con sus cupos
    """
    Recorre las clases SIN preguntar su tipo: cada objeto (Yoga, Spinning o
    Crossfit) responde cupos_disponibles() con su propia regla (polimorfismo).
    """
    print(f"{'N°':>4}  {'Tipo':<9} {'Dia':<10} {'Hora':<6} {'Dur.':>5} {'Cupo':>5} {'Inscr.':>6} {'Disp.':>6}  Instructor")  # Encabezado
    for c in clases:  # Recorre todas las clases mezcladas
        print(f"{c.id:>4}  {c.tipo:<9} {c.dia:<10} {c.hora:%H:%M}  {c.duracion_min:>3}m {c.cupo_maximo:>5} {c.inscritos:>6} "
              f"{c.cupos_disponibles():>6}  {instructores.get(c.instructor_rut, '-')}")  # cupos_disponibles(): cada tipo usa su regla


# =====================================================================
# Inicio de sesión
# =====================================================================

def iniciar_sesion(conexion):  # Pide RUT y contraseña; retorna el trabajador o None
    """
    El mensaje de error es siempre el mismo (no revela si el RUT existe) y tras
    5 intentos fallidos el programa se cierra.
    """
    titulo("INICIO DE SESION  (usuarios de prueba en el README · 0 = salir)")  # Título
    for intento in range(1, MAX_INTENTOS_LOGIN + 1):  # Máximo 5 intentos
        try:  # El 0 en el RUT permite salir
            rut = pedir_rut("RUT del trabajador (sin puntos): ")  # RUT validado
        except OperacionCancelada:  # Escribió 0
            return None  # Sale del programa
        clave = pedir_clave("Contraseña: ")  # Contraseña (no se ve al escribirla)
        trabajador = InstructorDao(conexion).buscar_por_rut(rut) or RecepcionistaDao(conexion).buscar_por_rut(rut)  # Busca en ambos roles
        if trabajador is None:  # Si el RUT no es de un trabajador...
            hashlib.pbkdf2_hmac("sha256", b"x", b"salt-ficticio", 260_000)  # ...gasta el mismo tiempo (no revela qué RUT existen)
        elif trabajador.login(clave):  # Compara con el hash guardado (PBKDF2 + comparación en tiempo constante)
            print(f"\nBienvenido/a, {trabajador.nombre} ({trabajador.rol}).")  # Saludo
            return trabajador  # Login correcto
        error(f"RUT o contraseña incorrectos. Intentos restantes: {MAX_INTENTOS_LOGIN - intento}.")  # Mensaje genérico
    print("\nDemasiados intentos fallidos. Por seguridad el programa se cerrara.")  # Bloqueo por fuerza bruta
    return None  # No se inició sesión


# =====================================================================
# Recepcionista: socios (CRUD)
# =====================================================================

def registrar_socio(conexion, usuario) -> None:  # CREAR socio
    titulo("REGISTRAR SOCIO  (0 = cancelar)")  # Título
    while True:  # El RUT se valida en el SETTER de Socio (módulo 11)
        texto = pedir_texto("RUT (sin puntos, ej: 12345678-5): ", largo_max=12)  # Lee el RUT
        try:  # Crea una ficha temporal para que los setters validen cada dato
            ficha = Socio(texto, "Por definir")  # El setter del RUT lanza ValueError si es inválido
        except ValueError as e:  # RUT rechazado por el setter
            error(f"{e}. Revise los numeros y el digito verificador.")  # Informa y vuelve a preguntar
            continue  # Pregunta de nuevo
        if SocioDao(conexion).existe(ficha.rut):  # No se permiten RUT duplicados
            error("Ya existe un socio con ese RUT.")  # Informa
            continue  # Pregunta de nuevo
        break  # RUT válido y nuevo
    pedir_con_setter("Nombre completo: ", lambda t: setattr(ficha, "nombre", t))  # Setter del nombre (obligatorio, máx. 80)
    pedir_con_setter("Correo (opcional, Enter para omitir): ", lambda t: setattr(ficha, "correo", t), obligatorio=False)  # Setter del correo
    pedir_con_setter("Telefono celular (opcional, ej: 912345678): ", lambda t: setattr(ficha, "telefono", t), obligatorio=False)  # Setter del teléfono
    print("Membresia inicial:")  # Dos formas de partir
    modo = pedir_opcion("Opcion: ", ["Pendiente de pago (se activa al cobrar la mensualidad)",
                                     "Ingresar fecha de vencimiento (socio que ya pago antes)"])  # Elige el modo
    inicio = vencimiento = None  # Por defecto: pendiente de pago
    if modo.startswith("Ingresar"):  # Si se indican fechas...
        vencimiento = pedir_fecha("Fecha de vencimiento (DD-MM-AAAA): ")  # Fecha validada
        inicio = vencimiento - timedelta(days=30)  # El período pagado fue de 30 días
    socio = Socio(ficha.rut, ficha.nombre, inicio, vencimiento, ficha.correo, ficha.telefono)  # Socio final (crea su Membresia)
    SocioDao(conexion).insertar(socio)  # Guarda socio + membresía en una transacción
    print(f"\nSocio guardado: {socio} · Membresia: {estado_membresia(socio)}.")  # Confirma


def listar_socios(conexion, usuario) -> None:  # LEER socios
    titulo("SOCIOS REGISTRADOS")  # Título
    socios = SocioDao(conexion).listar()  # Objetos Socio con su membresía (no diccionarios)
    print(f"{'RUT':<13} {'Nombre':<22} {'Correo':<26} {'Telefono':<10} Membresia")  # Encabezado
    for s in socios:  # Recorre los socios
        print(f"{s.rut_formateado:<13} {s.nombre[:22]:<22} {(s.correo or '-')[:26]:<26} {s.telefono or '-':<10} {estado_membresia(s)}")  # Una fila por socio
    print(f"\nTotal: {len(socios)} socios.")  # Cantidad


def modificar_socio(conexion, usuario) -> None:  # ACTUALIZAR socio
    titulo("MODIFICAR SOCIO  (Enter = mantener el valor actual · 0 = cancelar)")  # Título
    socio = buscar_socio(conexion)  # Busca por RUT
    if socio is None:  # Si no existe...
        return  # ...vuelve al menú
    for campo, etiqueta in (("nombre", "Nombre"), ("correo", "Correo"), ("telefono", "Telefono")):  # Datos que se pueden cambiar
        actual = getattr(socio, campo) or "-"  # Valor actual
        pedir_con_setter(  # El SETTER valida el valor nuevo
            f"{etiqueta} [{actual}]: ",  # Muestra el valor actual
            lambda t, c=campo: setattr(socio, c, t) if t else None,  # Enter (vacío) = no cambia
            obligatorio=False,  # Se puede dejar en blanco para mantener
        )
    SocioDao(conexion).actualizar(socio)  # Guarda los cambios (consulta parametrizada)
    print(f"\nCambios guardados: {socio.nombre} · {socio.correo or '-'} · {socio.telefono or '-'}")  # Confirma


def eliminar_socio(conexion, usuario) -> None:  # ELIMINAR socio
    titulo("ELIMINAR SOCIO  (0 = cancelar)")  # Título
    socio = buscar_socio(conexion)  # Busca por RUT
    if socio is None:  # Si no existe...
        return  # ...vuelve al menú
    inscripciones = InscripcionMensualDao(conexion).listar_por_socio(socio.rut)  # Historial que también se borrará
    print(f"Socio: {socio} · {estado_membresia(socio)} · {len(inscripciones)} inscripcion(es) registrada(s).")  # Muestra lo que se borrará
    if not pedir_si_no("¿Eliminar al socio y todo su historial? (s/n): "):  # Confirmación
        print("No se elimino nada.")  # Canceló
        return  # Vuelve al menú
    SocioDao(conexion).eliminar(socio.rut)  # Borra (membresía, inscripciones y asistencias en cascada)
    print(f"Socio {socio.rut_formateado} eliminado.")  # Confirma


def ver_ficha(conexion, usuario) -> None:  # Ficha completa de un socio
    titulo("FICHA DEL SOCIO  (0 = cancelar)")  # Título
    socio = buscar_socio(conexion)  # Busca por RUT
    if socio is None:  # Si no existe...
        return  # ...vuelve al menú
    print(f"{socio} · Correo: {socio.correo or '-'} · Telefono: {socio.telefono or '-'}")  # Datos personales
    print(f"Membresia: {estado_membresia(socio)}")  # Estado de la membresía
    mostrar_inscripciones(InscripcionMensualDao(conexion).listar_por_socio(socio.rut))  # Su historial con detalle


# =====================================================================
# Clases y cupos (polimorfismo)
# =====================================================================

def ver_cupos(conexion, usuario) -> None:  # Muestra las clases y cuántos socios más pueden inscribirse
    titulo(f"CLASES Y CUPOS DISPONIBLES ({mes_actual()})")  # Título
    clases = ClaseDao(conexion).listar(mes_actual())  # Clases con los inscritos del mes
    instructores = {i.rut: i.nombre for i in InstructorDao(conexion).listar()}  # RUT -> nombre
    mostrar_clases(clases, instructores)  # Tabla polimórfica
    print("\nReglas: Yoga = 20 - inscritos · Spinning = bicicletas operativas - inscritos · "
          "Crossfit = 12 - 2 reservados - inscritos")  # Cada tipo calcula distinto


def crear_clase(conexion, usuario) -> None:  # CREAR clase (solo instructor)
    titulo("CREAR CLASE  (0 = cancelar)")  # Título
    tipo = pedir_opcion("Tipo de clase: ", ["yoga", "spinning", "crossfit"])  # Tipo válido
    dia = pedir_opcion("Dia: ", list(DIAS_SEMANA))  # Día válido
    hora = pedir_hora("Hora de inicio (HH:MM, entre 06:00 y 22:00): ")  # Hora validada
    propias = ClaseDao(conexion).listar(mes_actual(), usuario.rut)  # Clases que ya dicta este instructor
    if any(c.dia == dia and c.hora == hora for c in propias):  # Un instructor no puede dictar dos clases a la vez
        error(f"Ya tiene una clase el {dia} a las {hora:%H:%M}. No se creo la clase.")  # Informa
        return  # Vuelve al menú
    clase = usuario.crear_clase(tipo, dia, hora)  # El MODELO crea el subtipo (solo el Instructor tiene este método)
    if isinstance(clase, Spinning):  # Spinning tiene un dato propio: las bicicletas que funcionan
        clase.bicicletas_operativas = pedir_entero(f"Bicicletas operativas (1 a {Spinning.CUPO_MAXIMO}): ", 1, Spinning.CUPO_MAXIMO)  # Rango validado
    DAO_POR_TIPO[tipo](conexion).insertar(clase)  # Guarda en la tabla padre y en la de su tipo
    print(f"\nClase creada: N° {clase.id} · {clase} · cupo maximo {clase.cupo_maximo} · {clase.duracion_min} min · "
          f"cupos disponibles {clase.cupos_disponibles()}")  # Confirma con la regla de su tipo


def elegir_clase_propia(conexion, usuario):  # Muestra las clases del instructor y elige una
    clases = ClaseDao(conexion).listar(mes_actual(), usuario.rut)  # Solo sus clases
    if not clases:  # Si no tiene...
        error("No tiene clases creadas.")  # ...lo informa
        return None  # Nada que elegir
    mostrar_clases(clases, {usuario.rut: usuario.nombre})  # Tabla de sus clases
    return elegir_clase(clases)  # Elige por N°


def modificar_clase(conexion, usuario) -> None:  # ACTUALIZAR clase (horario y bicicletas)
    titulo("MODIFICAR CLASE  (0 = cancelar)")  # Título
    clase = elegir_clase_propia(conexion, usuario)  # Solo puede modificar las propias
    if clase is None:  # Si no hay clase...
        return  # ...vuelve al menú
    dia = pedir_opcion("Nuevo dia: ", list(DIAS_SEMANA))  # Día válido
    hora = pedir_hora("Nueva hora (HH:MM): ")  # Hora validada
    ClaseDao(conexion).actualizar_horario(clase.id, dia, hora)  # Guarda el horario
    if isinstance(clase, Spinning):  # En Spinning también se actualizan las bicicletas
        bicis = pedir_entero(f"Bicicletas operativas (1 a {Spinning.CUPO_MAXIMO}): ", 1, Spinning.CUPO_MAXIMO)  # Rango validado
        SpinningDao(conexion).actualizar_bicicletas(clase.id, bicis)  # Guarda la cantidad
    print(f"Clase N° {clase.id} actualizada: {clase.tipo} {dia} {hora:%H:%M}.")  # Confirma


def eliminar_clase(conexion, usuario) -> None:  # ELIMINAR clase
    titulo("ELIMINAR CLASE  (0 = cancelar)")  # Título
    clase = elegir_clase_propia(conexion, usuario)  # Solo puede eliminar las propias
    if clase is None or not pedir_si_no(f"¿Eliminar {clase}? (s/n): "):  # Confirmación
        return  # Vuelve al menú
    try:  # La base de datos impide borrar una clase con reservas
        ClaseDao(conexion).eliminar(clase.id)  # Borra la clase
        print(f"Clase {clase} eliminada.")  # Confirma
    except sqlite3.IntegrityError:  # Tiene socios inscritos (llave foránea)
        error("No se puede eliminar: la clase tiene socios inscritos. Modifique su horario en su lugar.")  # Informa


# =====================================================================
# Inscripción mensual (la transacción con sus líneas de detalle)
# =====================================================================

def registrar_inscripcion(conexion, usuario) -> None:  # CREAR inscripción con detalle
    titulo("REGISTRAR INSCRIPCION MENSUAL  (0 = cancelar)")  # Título
    socio = buscar_socio(conexion)  # Busca por RUT
    if socio is None:  # Si no existe...
        return  # ...vuelve al menú
    mes = pedir_opcion("Mes: ", [mes_actual(), mes_siguiente()])  # Solo el mes actual o el siguiente
    dao = InscripcionMensualDao(conexion)  # DAO de inscripciones
    if dao.buscar(socio.rut, mes) is not None:  # Una inscripción por socio y mes
        error(f"{socio.nombre} ya tiene inscripcion para {mes}. Revise la opcion 'Ver detalle de inscripciones'.")  # Informa
        return  # Vuelve al menú
    clases = ClaseDao(conexion).listar(mes)  # Clases con los cupos de ese mes
    mostrar_clases(clases, {i.rut: i.nombre for i in InstructorDao(conexion).listar()})  # Muestra cupos
    ids = {c.id: c for c in clases}  # Diccionario id -> clase
    while True:  # Pide los N° hasta que sean válidos
        texto = leer("N° de las clases separados por coma (ej: 1,4): ")  # Lee la lista
        partes = [p.strip() for p in texto.split(",") if p.strip()]  # Separa por comas
        if not partes or not all(p.isdigit() and int(p) in ids for p in partes):  # Tipo y existencia
            error("Ingrese N° de la lista separados por coma (ej: 1,4).")  # Informa
            continue  # Vuelve a preguntar
        if len(set(partes)) != len(partes):  # No se puede reservar dos veces la misma clase
            error("No repita una misma clase.")  # Informa
            continue  # Vuelve a preguntar
        break  # Lista válida
    inscripcion = InscripcionMensual(socio, mes)  # AGREGACIÓN: recibe al socio que ya existe
    try:  # Las reglas del negocio pueden impedir la operación
        for p in partes:  # Recorre las clases elegidas
            inscripcion.agregar_clase(ids[int(p)])  # COMPOSICIÓN: crea cada DetalleClaseReservada (lanza CupoLlenoException)
        dao.guardar(inscripcion, usuario.rut)  # Guarda cabecera + detalles en UNA transacción (revisa el cupo otra vez)
    except CupoLlenoException as e:  # Regla 1: clase llena
        error(f"Inscripcion impedida: {e}. No se guardo nada.")  # Informa y el programa sigue
        return  # Vuelve al menú
    print(f"\nInscripcion N° {inscripcion.id} guardada (pendiente de pago):")  # Confirma
    mostrar_inscripciones([inscripcion])  # Muestra sus líneas de detalle y el total


def mostrar_inscripciones(inscripciones: list) -> None:  # Muestra inscripciones con sus líneas de detalle
    if not inscripciones:  # Si no hay...
        print("  (sin inscripciones)")  # ...lo indica
    for i in inscripciones:  # Recorre las inscripciones
        print(f"\n  Inscripcion N° {i.id} · {i.socio.nombre} · mes {i.mes} · {'PAGADA' if i.pagada else 'pendiente de pago'}")  # Cabecera
        for numero, d in enumerate(i.detalles, start=1):  # Recorre las líneas de detalle
            print(f"    Linea {numero}: {d.resumen():<28} {pesos(d.subtotal):>9}")  # Una línea por clase reservada
        print(f"    {'TOTAL':<36} {pesos(i.calcular_total()):>9}")  # Total de la transacción


def ver_inscripciones(conexion, usuario) -> None:  # LEER inscripciones con su detalle
    titulo("DETALLE DE INSCRIPCIONES  (0 = cancelar)")  # Título
    socio = buscar_socio(conexion)  # Busca por RUT
    if socio is not None:  # Si existe...
        mostrar_inscripciones(InscripcionMensualDao(conexion).listar_por_socio(socio.rut))  # ...muestra su historial


def elegir_inscripcion_pendiente(conexion, socio):  # Elige una inscripción sin pagar del socio
    pendientes = [i for i in InscripcionMensualDao(conexion).listar_por_socio(socio.rut) if not i.pagada]  # Solo las no pagadas
    if not pendientes:  # Si no tiene...
        error(f"{socio.nombre} no tiene inscripciones pendientes de pago.")  # ...lo informa
        return None  # Nada que elegir
    mostrar_inscripciones(pendientes)  # Las muestra con su detalle
    if len(pendientes) == 1:  # Si hay una sola...
        return pendientes[0]  # ...se elige sola
    elegida = pedir_entero("N° de la inscripcion: ", 1, 999999)  # Número de inscripción
    for i in pendientes:  # Busca la inscripción elegida
        if i.id == elegida:  # Si está en la lista...
            return i  # ...la retorna
    error("Ese N° no esta en la lista.")  # Informa
    return None  # No se eligió ninguna


def cobrar_mensualidad(conexion, usuario) -> None:  # ACTUALIZAR inscripción: registrar el pago
    titulo("COBRAR MENSUALIDAD  (0 = cancelar)")  # Título
    socio = buscar_socio(conexion)  # Busca por RUT
    inscripcion = elegir_inscripcion_pendiente(conexion, socio) if socio else None  # Inscripción a cobrar
    if inscripcion is None:  # Si no hay...
        return  # ...vuelve al menú
    total = inscripcion.calcular_total()  # Monto a cobrar
    recibido = pedir_entero(f"Monto recibido en pesos (total {pesos(total)}): ", total, 10_000_000)  # Tipo y rango: no menos que el total
    try:  # El modelo valida el cobro
        cobrado = usuario.cobrar_mensualidad(inscripcion)  # Marca pagada y renueva la membresía
        InscripcionMensualDao(conexion).registrar_pago(inscripcion, cobrado, usuario.rut)  # Guarda pago + membresía en una transacción
    except ValueError as e:  # Ya pagada o mes terminado
        error(str(e))  # Informa
        return  # Vuelve al menú
    print(f"\nCobro registrado: {pesos(cobrado)} · vuelto {pesos(recibido - cobrado)} · {estado_membresia(inscripcion.socio)}")  # Confirma


def anular_inscripcion(conexion, usuario) -> None:  # ELIMINAR inscripción (solo si no está pagada)
    titulo("ANULAR INSCRIPCION  (0 = cancelar)")  # Título
    socio = buscar_socio(conexion)  # Busca por RUT
    inscripcion = elegir_inscripcion_pendiente(conexion, socio) if socio else None  # Solo las no pagadas se pueden anular
    if inscripcion is None or not pedir_si_no("¿Anular esta inscripcion? (s/n): "):  # Confirmación
        return  # Vuelve al menú
    InscripcionMensualDao(conexion).eliminar(inscripcion.id)  # Borra cabecera y detalles (cascada)
    print(f"Inscripcion N° {inscripcion.id} anulada: sus cupos quedaron libres.")  # Confirma


# =====================================================================
# Control de ingreso y suplementos
# =====================================================================

def control_ingreso(conexion, usuario) -> None:  # Regla 2: no entra un socio con la membresía vencida
    titulo("CONTROL DE INGRESO  (0 = cancelar)")  # Título
    socio = buscar_socio(conexion)  # Busca por RUT
    if socio is None:  # Si no existe...
        return  # ...vuelve al menú
    try:  # La regla puede impedir la operación
        socio.puede_ingresar()  # Lanza MembresiaVencidaException si no está vigente
        print(f"PUEDE INGRESAR: {socio} · {estado_membresia(socio)}")  # Ingreso permitido
    except MembresiaVencidaException as e:  # Regla 2: membresía vencida o sin pagar
        error(f"INGRESO IMPEDIDO: {e}. Debe pagar su mensualidad.")  # Informa y el programa sigue


def obtener_dolar(conexion):  # Consulta el dólar del día e informa si la API falló
    DolarService.limpiar_cache()  # En la consola cada consulta va a la API: así se ve el valor real de este momento
    cotizacion = DolarService(conexion).obtener_cotizacion()  # API mindicador.cl (requests, timeout de 5 s)
    if cotizacion.fuente == "api":  # Valor real del día
        print(f"Dolar observado: {dolar(cotizacion.valor)} · fuente: API mindicador.cl · fecha {cotizacion.fecha}")  # Muestra el valor
    else:  # La API falló: se informa el motivo
        error(f"No se pudo obtener el dolar del dia: {cotizacion.aviso}.")  # Motivo (sin conexión, demora o respuesta inesperada)
        origen = f"ultimo valor guardado ({cotizacion.fecha})" if cotizacion.fuente == "respaldo" else "valor por defecto"  # De dónde sale el valor
        print(f"      Se usa el {origen}: {dolar(cotizacion.valor)}. El programa sigue funcionando.")  # El sistema continúa
    return cotizacion  # Retorna la cotización usada


def ver_suplementos(conexion, usuario) -> None:  # Precio de los suplementos con el dólar del día
    titulo("SUPLEMENTOS IMPORTADOS · PRECIO CON EL DOLAR DEL DIA")  # Título
    cotizacion = obtener_dolar(conexion)  # Dólar del día (o respaldo informado)
    dao = SuplementoDao(conexion)  # DAO de suplementos
    suplementos = dao.listar()  # Objetos Suplemento
    print(f"\n{'Codigo':<9} {'Producto':<28} {'USD':>7}   x dolar   = {'Precio CLP':>11} {'Stock':>6}")  # Encabezado
    for s in suplementos:  # Recorre los productos
        s.actualizar_precio(cotizacion.valor)  # El MODELO calcula el precio en pesos con el dólar
        print(f"{s.codigo:<9} {s.nombre[:28]:<28} {s.precio_usd:>7.2f}   x {cotizacion.valor:>7.2f} = {pesos(s.precio_clp):>11} {s.stock:>6}")  # Fila
    dao.actualizar_precios(suplementos)  # Guarda los precios recalculados


def vender_suplemento(conexion, usuario) -> None:  # Venta de un suplemento
    titulo("VENDER SUPLEMENTO  (0 = cancelar)")  # Título
    ver_suplementos(conexion, usuario)  # Muestra precios actualizados
    dao = SuplementoDao(conexion)  # DAO de suplementos
    while True:  # Pide un código que exista
        suplemento = dao.buscar(pedir_texto("\nCodigo del producto: ", largo_max=20).upper())  # Busca (consulta parametrizada)
        if suplemento is not None:  # Si existe...
            break  # ...sigue
        error("No existe un producto con ese codigo.")  # Informa
    if suplemento.stock == 0:  # Sin stock no se vende
        error(f"{suplemento.nombre} no tiene stock.")  # Informa
        return  # Vuelve al menú
    cantidad = pedir_entero(f"Cantidad (1 a {suplemento.stock}): ", 1, suplemento.stock)  # Tipo y rango (no más que el stock)
    valor_dolar = DolarService(conexion).obtener_valor()  # Dólar ya consultado (caché)
    suplemento.actualizar_precio(valor_dolar)  # Precio en pesos de hoy
    total = usuario.vender_suplemento(suplemento, cantidad)  # El modelo valida y descuenta stock
    dao.registrar_venta(suplemento, cantidad, total, valor_dolar, usuario.rut)  # Guarda venta + stock (atómico)
    print(f"Venta registrada: {cantidad} x {suplemento.nombre} = {pesos(total)} · stock restante {suplemento.stock}")  # Confirma


# =====================================================================
# Instructor: asistencia
# =====================================================================

def registrar_asistencia(conexion, usuario) -> None:  # Marca la asistencia de un socio a una clase
    titulo("REGISTRAR ASISTENCIA  (0 = cancelar)")  # Título
    clase = elegir_clase_propia(conexion, usuario)  # Solo sus clases
    if clase is None:  # Si no hay...
        return  # ...vuelve al menú
    inscritos = InscripcionMensualDao(conexion).listar_socios_de_clase(clase.id, mes_actual())  # Socios inscritos este mes
    if not inscritos:  # Si nadie está inscrito...
        error("La clase no tiene socios inscritos este mes.")  # ...lo informa
        return  # Vuelve al menú
    socio = pedir_opcion("Socio presente: ", [str(s) for s in inscritos])  # Elige de la lista
    socio = inscritos[[str(s) for s in inscritos].index(socio)]  # Recupera el objeto Socio elegido
    try:  # Las reglas pueden impedir la operación
        usuario.marcar_asistencia(clase, socio)  # Valida que la clase sea suya y que la membresía esté vigente
        AsistenciaDao(conexion).registrar(clase.id, socio.rut, usuario.rut)  # Guarda (una vez por día)
        print(f"Asistencia registrada: {socio.nombre} en {clase}.")  # Confirma
    except MembresiaVencidaException as e:  # Regla 2 también en la asistencia
        error(f"Asistencia impedida: {e}.")  # Informa
    except (ValueError, PermissionError) as e:  # Ya registrada hoy o clase de otro instructor
        error(str(e))  # Informa


def demostracion(conexion, usuario) -> None:  # Demo del modelo de la Evaluación Sumativa N°2
    from demo_modelo import main as demo  # Se importa solo cuando se usa
    demo()  # Ejecuta la demostración (en memoria, no toca la base de datos)


# =====================================================================
# Menús por rol
# =====================================================================

MENU_RECEPCIONISTA = {  # Opción -> (texto, función)
    "1": ("Registrar socio", registrar_socio),
    "2": ("Listar socios", listar_socios),
    "3": ("Modificar socio (nombre, correo o telefono)", modificar_socio),
    "4": ("Eliminar socio", eliminar_socio),
    "5": ("Ver ficha de un socio", ver_ficha),
    "6": ("Ver clases y cupos disponibles", ver_cupos),
    "7": ("Registrar inscripcion mensual", registrar_inscripcion),
    "8": ("Ver detalle de inscripciones de un socio", ver_inscripciones),
    "9": ("Cobrar mensualidad", cobrar_mensualidad),
    "10": ("Anular inscripcion no pagada", anular_inscripcion),
    "11": ("Control de ingreso", control_ingreso),
    "12": ("Suplementos: precio con el dolar del dia", ver_suplementos),
    "13": ("Vender suplemento", vender_suplemento),
    "D": ("Demostracion del modelo (Evaluacion N°2)", demostracion),
}

MENU_INSTRUCTOR = {  # Opción -> (texto, función)
    "1": ("Ver clases y cupos disponibles", ver_cupos),
    "2": ("Crear clase (Yoga, Spinning o Crossfit)", crear_clase),
    "3": ("Modificar horario de una clase", modificar_clase),
    "4": ("Eliminar clase", eliminar_clase),
    "5": ("Registrar asistencia", registrar_asistencia),
    "D": ("Demostracion del modelo (Evaluacion N°2)", demostracion),
}


def menu(conexion, usuario) -> str:  # Muestra el menú del rol hasta que el usuario sale o cambia de usuario
    opciones = MENU_RECEPCIONISTA if usuario.rol == "recepcionista" else MENU_INSTRUCTOR  # Cada rol ve solo sus opciones
    while True:  # Bucle principal del menú
        titulo(f"POWERFIT · MENU {usuario.rol.upper()} · {usuario.nombre}")  # Título con el rol
        for clave, (texto, _) in opciones.items():  # Muestra las opciones
            print(f" {clave:>2}. {texto}")  # Ej: " 1. Registrar socio"
        print("  C. Cambiar de usuario")  # Volver al login sin cerrar el programa
        print("  0. Salir")  # Terminar
        eleccion = input("Opcion: ").strip().upper()  # Lee la opción
        if eleccion == "0":  # Salir
            return "salir"  # Termina el programa
        if eleccion == "C":  # Cambiar de usuario
            return "cambiar"  # Vuelve al login
        if eleccion not in opciones:  # Opción inexistente (ej: 99)
            error(f"La opcion '{eleccion}' no existe. Elija una opcion del menu.")  # Informa y vuelve a mostrar el menú
            continue  # Vuelve al menú
        texto, accion = opciones[eleccion]  # Función elegida
        try:  # Ningún error detiene el programa
            accion(conexion, usuario)  # Ejecuta la opción
        except OperacionCancelada:  # El usuario escribió 0
            print("Operacion cancelada.")  # Informa
        except ValueError as e:  # Dato rechazado por el modelo
            error(str(e))  # Informa
        except sqlite3.Error as e:  # Problema de base de datos
            error(f"No se pudo completar la operacion en la base de datos ({e}).")  # Informa sin cerrar el programa


def main() -> None:  # Punto de entrada del programa
    print("POWERFIT · Sistema de gestion del gimnasio (consola)")  # Encabezado
    conexion = conectar.crear_conexion()  # Abre (o crea) powerfit.db
    crear_esquema(conexion)  # Crea las tablas si no existen: corre en un computador nuevo
    if cargar_datos_demo(conexion):  # Si la base de datos estaba vacía...
        print("Base de datos nueva: se cargaron trabajadores, clases, socios y suplementos de ejemplo.")  # ...lo informa
    try:  # Ctrl+C o fin de la entrada cierran el programa de forma ordenada
        while True:  # Permite cambiar de usuario sin cerrar el programa
            usuario = iniciar_sesion(conexion)  # Login
            if usuario is None or menu(conexion, usuario) == "salir":  # Salió o no pudo entrar
                break  # Termina
    except (KeyboardInterrupt, EOFError):  # El usuario cerró la entrada
        print()  # Salto de línea
    finally:  # Siempre se cierra la conexión
        conexion.close()  # Cierra la base de datos
    print("Programa finalizado. ¡Hasta pronto!")  # Despedida


if __name__ == "__main__":  # Solo se ejecuta si se llama directamente: python main.py
    main()  # Inicia el programa
