"""
Clase Recepcionista: hereda de Trabajador.
Inscribe socios, cobra mensualidades y vende suplementos.

IMPORTANTE: NO tiene métodos para crear ni modificar clases. La restricción
del requerimiento 2 queda expresada en la propia estructura de la clase.
"""

from __future__ import annotations  # Permite usar anotaciones modernas (str | None) también en Python 3.7 a 3.9

import calendar  # Librería estándar para saber cuántos días tiene un mes
from datetime import date  # Importa el tipo fecha
from model.trabajador import Trabajador  # Importa la clase base abstracta
from model.socio import Socio  # Importa Socio
from model.inscripcion_mensual import InscripcionMensual  # Importa InscripcionMensual
from model.suplemento import Suplemento  # Importa Suplemento


class Recepcionista(Trabajador):  # Recepcionista ES UN Trabajador (herencia)
    """
    Trabajadora del mesón: socios, cobros y venta de suplementos.
    """

    def __init__(self, rut: str, nombre: str, password_hash: str) -> None:  # Constructor propio del subtipo
        super().__init__(rut, nombre, password_hash)  # Llama al constructor de la clase base Trabajador

    @property
    def rol(self) -> str:  # Implementa la propiedad abstracta del padre
        return "recepcionista"  # Rol usado por el control de acceso de la web

    def inscribir_socio(self, rut: str, nombre: str) -> Socio:  # Método del UML
        """
        Crea la ficha de un socio nuevo. Si el RUT es inválido,
        el constructor de Socio lanza ValueError y la ficha no se crea.
        """
        return Socio(rut, nombre)  # Crea el socio (con su membresía pendiente de pago)

    def cobrar_mensualidad(self, i: InscripcionMensual, hoy: date | None = None) -> int:  # Método del UML
        """
        Cobra la inscripción del mes, la marca como pagada y extiende la
        membresía del socio hasta el último día de ese mes.
        Retorna el monto cobrado en pesos.
        """
        if i.pagada:  # Evita cobrar dos veces la misma inscripción
            raise ValueError("Esta inscripcion ya fue pagada")  # Rechaza el doble cobro
        total = i.calcular_total()  # Calcula el total sumando las clases reservadas
        anio, mes = map(int, i.mes.split("-"))  # Separa el año y el mes de "AAAA-MM"
        ultimo_dia = calendar.monthrange(anio, mes)[1]  # Obtiene el último día de ese mes (28, 29, 30 o 31)
        fin_de_mes = date(anio, mes, ultimo_dia)  # Fecha hasta la que quedará cubierta la membresía
        if fin_de_mes < (hoy or date.today()):  # No se cobra un mes que ya terminó
            raise ValueError(f"El mes {i.mes} ya termino, no se puede cobrar")  # Rechaza ANTES de modificar nada
        i.marcar_pagada()  # Marca la inscripción como pagada (valida que tenga al menos 1 clase)
        i.socio.membresia.renovar_hasta(fin_de_mes, hoy)  # Extiende la membresía hasta fin de mes
        return total  # Retorna el monto cobrado

    def vender_suplemento(self, s: Suplemento, cant: int) -> int:  # Método del UML
        """
        Vende 'cant' unidades de un suplemento y retorna el total en pesos.
        """
        return s.vender(cant)  # Delega en el suplemento, que valida stock y precio
