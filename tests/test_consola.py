"""
Pruebas del programa por consola (main.py) siguiendo el GUION DE PRUEBAS del
docente (P01 a P19). Se simula lo que el usuario escribe por teclado y se
revisa lo que el programa muestra en pantalla.

Cada prueba usa una base de datos temporal (nunca toca powerfit.db) y la API
del dólar "caída" (fixture sin_internet de conftest.py), salvo la P16 que
simula una respuesta real de mindicador.cl.
"""

import builtins  # Para reemplazar input() por las respuestas del guion
import pytest  # Framework de pruebas
import main  # Programa principal por consola
from services.dolar_service import DolarService  # Para simular la API del dólar

RECEPCION = ["22222222-2", "Recepcion123!"]  # Login de la recepcionista (sin puntos)
INSTRUCTOR = ["11111111-1", "Instructor123!"]  # Login de la instructora


@pytest.fixture
def bd_temporal(tmp_path, monkeypatch):  # Base de datos nueva para cada prueba
    monkeypatch.setenv("POWERFIT_DB", str(tmp_path / "consola.db"))  # conectar.py usa esta variable
    return tmp_path / "consola.db"  # Ruta del archivo


def ejecutar(monkeypatch, capsys, entradas: list[str]) -> str:  # Corre main() con las entradas indicadas
    respuestas = iter(entradas)  # Respuestas en orden
    monkeypatch.setattr(builtins, "input", lambda mensaje="": next(respuestas))  # input() devuelve la siguiente respuesta
    main.main()  # Ejecuta el programa completo (al acabarse las respuestas termina con EOF de forma ordenada)
    return capsys.readouterr().out  # Retorna todo lo que se mostró en pantalla


def test_p01_a_p06_crud_de_socio_y_persistencia(bd_temporal, monkeypatch, capsys):  # P01-P06
    salida = ejecutar(monkeypatch, capsys, RECEPCION + [
        "1", "12.345.678-5", "Pedro Soto", "", "", "1",  # P02: crear socio (con puntos, como el guion)
        "2",  # P03: listar
        "3", "12345678-5", "", "pedro.soto@correo.cl", "912345678",  # P04: modificar correo y teléfono
        "2",  # Listar para ver el cambio
        "0",  # Salir
    ])
    assert "MENU RECEPCIONISTA" in salida  # P01: el programa inicia y muestra el menú
    assert "Socio guardado: Pedro Soto (12.345.678-5)" in salida  # P02: confirma que se guardó
    assert salida.count("Pedro Soto") >= 3 and "pedro.soto@correo.cl" in salida  # P03 y P04: aparece y con el cambio
    salida = ejecutar(monkeypatch, capsys, RECEPCION + ["2", "4", "12345678-5", "s", "2", "0"])  # P05 (reabrir) y P06 (eliminar)
    listado_al_reabrir, listado_final = salida.split("ELIMINAR SOCIO")[0], salida.split("eliminado.")[1]  # Antes y después de eliminar
    assert "pedro.soto@correo.cl" in listado_al_reabrir  # P05: el registro sigue ahí tras cerrar y abrir
    assert "Pedro Soto" not in listado_final  # P06: ya no aparece


def test_p07_p08_rut_correcto_e_incorrecto(bd_temporal, monkeypatch, capsys):  # P07-P08
    salida = ejecutar(monkeypatch, capsys, RECEPCION + [
        "1", "12.345.678-9",  # P08: dígito verificador incorrecto
        "12.345.678-5", "Pedro Soto", "", "", "1",  # P07: el correcto se acepta
        "0",
    ])
    assert "RUT invalido: 12.345.678-9" in salida  # Lo rechaza con un mensaje...
    assert "Socio guardado: Pedro Soto" in salida  # ...el programa sigue y acepta el correcto


def test_p09_a_p11_tres_tipos_con_su_cupo(bd_temporal, monkeypatch, capsys):  # P09-P11 (como instructora)
    salida = ejecutar(monkeypatch, capsys, INSTRUCTOR + [
        "2", "1", "1", "10:00",  # P09: Yoga lunes 10:00
        "2", "2", "3", "07:00", "10",  # P10: Spinning miércoles 07:00 con 10 bicicletas
        "2", "3", "5", "07:00",  # P11: Crossfit viernes 07:00
        "0",
    ])
    assert "Yoga lunes 10:00 · cupo maximo 20 · 60 min · cupos disponibles 20" in salida  # P09
    assert "Spinning miercoles 07:00 · cupo maximo 15 · 45 min · cupos disponibles 10" in salida  # P10: distinto a Yoga
    assert "Crossfit viernes 07:00 · cupo maximo 12 · 50 min · cupos disponibles 10" in salida  # P11: 2 reservados


def test_p12_p13_p14_inscripcion_con_detalle_y_cupo_lleno(bd_temporal, monkeypatch, capsys):  # P12-P14
    salida = ejecutar(monkeypatch, capsys, RECEPCION + [
        "1", "12345678-5", "Pedro Soto", "", "", "1",  # Socio de prueba
        "7", "12345678-5", "1", "1,6",  # P12: Yoga lunes (N° 1) + Crossfit miércoles (N° 6)
        "8", "12345678-5",  # P13: ver el detalle
        "7", "24681357-4", "1", "3",  # P14: Florencia al Crossfit del viernes, que está lleno
        "0",
    ])
    assert "guardada (pendiente de pago)" in salida  # P12: un solo registro de inscripción
    assert "Linea 1: Yoga · lunes 09:00" in salida and "Linea 2: Crossfit · miercoles 20:00" in salida  # P13: sus líneas
    assert "TOTAL" in salida and "$37.000" in salida  # Total: 15.000 + 22.000
    assert "Inscripcion impedida" in salida and "No se guardo nada" in salida  # P14: se impide
    assert salida.rstrip().endswith("¡Hasta pronto!")  # El programa siguió hasta salir normalmente


def test_p15_ingreso_con_membresia_vencida(bd_temporal, monkeypatch, capsys):  # P15
    salida = ejecutar(monkeypatch, capsys, RECEPCION + [
        "1", "11222333-9", "Socio Vencido", "", "", "2", "01-09-2026",  # Membresía con fecha anterior a hoy
        "11", "11222333-9",  # Registrar su ingreso
        "0",
    ])
    assert "INGRESO IMPEDIDO" in salida and "vencio el 01-09-2026" in salida  # Se impide e informa
    assert "MENU RECEPCIONISTA" in salida.split("INGRESO IMPEDIDO")[1]  # El programa sigue (vuelve al menú)


def test_p16_precio_con_el_dolar_del_dia(bd_temporal, monkeypatch, capsys):  # P16 (API simulada con valor real)
    monkeypatch.setattr(DolarService, "_obtener_json_desde_api",  # Respuesta con el formato de mindicador.cl
                        lambda self: {"serie": [{"fecha": "2026-10-10T03:00:00.000Z", "valor": 940.5}]})
    salida = ejecutar(monkeypatch, capsys, RECEPCION + ["12", "0"])  # Ver precios de suplementos
    assert "Dolar observado: $940,50 · fuente: API mindicador.cl" in salida  # Usa el valor de la API
    assert "45.00   x  940.50 =     $42.322" in salida  # Proteína: 45 USD x 940,50 = $42.322


def test_p17_sin_internet_avisa_y_sigue(bd_temporal, monkeypatch, capsys):  # P17 (la API "caída" por conftest)
    salida = ejecutar(monkeypatch, capsys, RECEPCION + ["12", "0"])  # Ver precios sin conexión
    assert "No se pudo obtener el dolar del dia: no hay conexion con la API" in salida  # Avisa el motivo
    assert "El programa sigue funcionando" in salida and "¡Hasta pronto!" in salida  # Y no se cae


def test_p18_p19_opcion_inexistente_y_letras_en_un_numero(bd_temporal, monkeypatch, capsys):  # P18-P19
    salida = ejecutar(monkeypatch, capsys, RECEPCION + [
        "99",  # P18: opción que no existe
        "1", "12345678-5", "Pedro Soto", "", "", "1",
        "7", "12345678-5", "1", "1",  # Inscripción de $15.000
        "9", "12345678-5", "abc", "100", "20000",  # P19: letras en el monto, luego un monto bajo, luego uno válido
        "C",  # Cambiar de usuario
    ] + INSTRUCTOR + [
        "2", "2", "1", "08:00", "abc", "99", "12",  # P19: letras y fuera de rango en las bicicletas (cupo)
        "0",
    ])
    assert "La opcion '99' no existe" in salida  # P18: mensaje y vuelve al menú
    assert "Debe ingresar un numero entero" in salida  # P19: letras rechazadas
    assert "El numero debe estar entre 15000" in salida  # Rango del monto (no menos que el total)
    assert "Cobro registrado: $15.000 · vuelto $5.000" in salida  # Siguió y cobró
    assert "El numero debe estar entre 1 y 15" in salida  # Rango de bicicletas
    assert "Spinning lunes 08:00 · cupo maximo 15 · 45 min · cupos disponibles 12" in salida  # Siguió y creó la clase


def test_login_incorrecto_y_permisos_por_rol(bd_temporal, monkeypatch, capsys):  # Autenticación
    salida = ejecutar(monkeypatch, capsys, ["22222222-2", "mala"] + RECEPCION + ["0"])  # Una clave mala y luego la correcta
    assert "RUT o contraseña incorrectos. Intentos restantes: 4" in salida  # Mensaje genérico
    assert "Crear clase" not in salida  # La recepcionista no ve la opción de crear clases
    salida = ejecutar(monkeypatch, capsys, ["22222222-2", "x"] * 5)  # Cinco intentos fallidos
    assert "Demasiados intentos fallidos" in salida  # Se cierra por seguridad
