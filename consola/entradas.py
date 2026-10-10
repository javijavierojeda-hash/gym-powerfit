"""
Lectura SEGURA de datos por teclado para el menú de consola.

Regla de seguridad: ninguna entrada del usuario se usa sin validarla antes
(tipo, formato y rango). Si el dato es inválido se muestra un mensaje y se
vuelve a preguntar: el programa nunca se cae por un dato mal escrito.

Cada función retorna un valor ya validado y del tipo correcto (int, date,
time, str...). Escribir "0" donde se indica permite cancelar la operación.
"""

from __future__ import annotations  # Permite usar anotaciones modernas (str | None) también en Python 3.7 a 3.9

import getpass  # Lee la contraseña sin mostrarla en pantalla
import sys  # Para saber si hay una terminal interactiva
from datetime import date, time  # Tipos de fecha y hora que se validan
from model.validaciones import es_rut_valido, limpiar_rut  # Validación del RUT (módulo 11)

CANCELAR = "0"  # Texto que el usuario escribe para cancelar una operación


class OperacionCancelada(Exception):  # Excepción propia: el usuario escribió 0 para cancelar
    """Se lanza cuando el usuario decide cancelar la operación en curso."""


def leer(mensaje: str) -> str:  # Lee una línea del teclado
    """
    Lee lo que escribe el usuario y le quita los espacios de los extremos.
    Si escribe 0, la operación se cancela.
    """
    texto = input(mensaje).strip()  # Lee y limpia la entrada
    if texto == CANCELAR:  # Si el usuario quiere cancelar...
        raise OperacionCancelada()  # ...se interrumpe la operación (el menú lo informa)
    return texto  # Retorna el texto limpio


def error(mensaje: str) -> None:  # Muestra un error de validación con un formato común
    print(f"  [!] {mensaje}")  # El prefijo [!] permite distinguir los errores


def pedir_texto(mensaje: str, obligatorio: bool = True, largo_max: int = 80) -> str:  # Texto libre con largo máximo
    while True:  # Repite hasta que el dato sea válido
        texto = leer(mensaje)  # Lee el texto
        if not texto and obligatorio:  # Campo obligatorio vacío
            error("Este dato es obligatorio.")  # Informa
        elif len(texto) > largo_max:  # Rango: largo máximo
            error(f"Maximo {largo_max} caracteres.")  # Informa
        else:  # Dato válido
            return texto  # Lo retorna


def pedir_entero(mensaje: str, minimo: int, maximo: int) -> int:  # Número entero dentro de un rango
    while True:  # Repite hasta que el dato sea válido
        texto = leer(mensaje)  # Lee el texto
        if not texto.isdigit():  # Tipo: solo dígitos (rechaza letras, signos y decimales)
            error(f"Debe ingresar un numero entero entre {minimo} y {maximo}.")  # Informa
            continue  # Vuelve a preguntar
        numero = int(texto)  # Convierte a entero (seguro: ya se revisó que son dígitos)
        if not minimo <= numero <= maximo:  # Rango permitido
            error(f"El numero debe estar entre {minimo} y {maximo}.")  # Informa
            continue  # Vuelve a preguntar
        return numero  # Retorna el número validado


def pedir_rut(mensaje: str = "RUT (sin puntos, ej: 12345678-5): ") -> str:  # RUT chileno válido
    while True:  # Repite hasta que el dato sea válido
        texto = leer(mensaje)  # Lee el RUT
        if es_rut_valido(texto):  # Formato y dígito verificador (módulo 11)
            return limpiar_rut(texto)  # Retorna el RUT normalizado (12345678-5)
        error("RUT invalido: revise los numeros y el digito verificador.")  # Informa


def pedir_fecha(mensaje: str, permitir_vacio: bool = False) -> date | None:  # Fecha en formato DD-MM-AAAA
    while True:  # Repite hasta que el dato sea válido
        texto = leer(mensaje)  # Lee la fecha
        if not texto and permitir_vacio:  # Si se permite dejarla en blanco...
            return None  # ...retorna None
        try:  # Intenta interpretar la fecha
            dia, mes, anio = (int(parte) for parte in texto.replace("/", "-").split("-"))  # Separa día, mes y año
            fecha = date(anio, mes, dia)  # date() valida que la fecha exista (ej: rechaza 31-02)
        except ValueError:  # Formato o fecha inexistente
            error("Fecha invalida. Use el formato DD-MM-AAAA (ej: 15-09-2026).")  # Informa
            continue  # Vuelve a preguntar
        if not 2000 <= fecha.year <= date.today().year + 1:  # Rango razonable de años
            error("El año debe estar entre 2000 y el proximo año.")  # Informa
            continue  # Vuelve a preguntar
        return fecha  # Retorna la fecha validada


def pedir_hora(mensaje: str) -> time:  # Hora en formato HH:MM
    while True:  # Repite hasta que el dato sea válido
        texto = leer(mensaje)  # Lee la hora
        try:  # Intenta interpretar la hora
            hora = time.fromisoformat(texto)  # Acepta HH:MM (valida 0-23 y 0-59)
        except ValueError:  # Formato inválido
            error("Hora invalida. Use el formato HH:MM (ej: 18:30).")  # Informa
            continue  # Vuelve a preguntar
        if not time(6, 0) <= hora <= time(22, 0):  # Rango: horario de funcionamiento del gimnasio
            error("El gimnasio funciona entre las 06:00 y las 22:00.")  # Informa
            continue  # Vuelve a preguntar
        return hora.replace(second=0, microsecond=0)  # Retorna la hora sin segundos


def pedir_opcion(mensaje: str, opciones: list[str]) -> str:  # Elige una opción de una lista cerrada
    while True:  # Repite hasta que el dato sea válido
        for numero, texto in enumerate(opciones, start=1):  # Muestra las opciones numeradas
            print(f"   {numero}. {texto}")  # Ej: "1. lunes"
        numero = pedir_entero(mensaje, 1, len(opciones))  # Pide un número dentro del rango
        return opciones[numero - 1]  # Retorna el texto de la opción elegida


def pedir_si_no(mensaje: str) -> bool:  # Pregunta de sí o no
    while True:  # Repite hasta que el dato sea válido
        texto = input(mensaje).strip().lower()  # Lee la respuesta (aquí el 0 no cancela)
        if texto in ("s", "si", "sí"):  # Respuestas afirmativas
            return True  # Sí
        if texto in ("n", "no"):  # Respuestas negativas
            return False  # No
        error("Responda s (si) o n (no).")  # Informa


def pedir_clave(mensaje: str = "Contraseña: ") -> str:  # Contraseña sin mostrarla en pantalla
    if sys.stdin.isatty():  # Si hay una terminal real...
        return getpass.getpass(mensaje)  # ...la contraseña no se ve al escribirla
    return input(mensaje)  # Sin terminal (pruebas automáticas): se lee normal
