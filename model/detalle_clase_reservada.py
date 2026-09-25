"""
Clase DetalleClaseReservada: cada clase reservada dentro de una inscripción mensual.

Es la "línea de detalle" de la transacción (como LineaDetalle en el repo del
profesor). No tiene sentido fuera de su inscripción (composición en el UML).
"""

from datetime import time  # Importa el tipo hora
from model.clase import Clase  # Importa la clase base para el type hint


class DetalleClaseReservada:  # Define la clase del detalle
    """
    Guarda qué clase se reservó y en qué día y hora.
    """

    def __init__(self, clase: Clase, dia: str | None = None, hora: time | None = None) -> None:  # Constructor
        if not isinstance(clase, Clase):  # Valida que se reciba una clase real del gimnasio
            raise TypeError("El detalle debe referirse a una Clase")  # Evita detalles con datos inválidos
        self.__clase: Clase = clase  # ASOCIACIÓN: el detalle apunta a la clase, pero no la contiene
        self.__dia: str = dia or clase.dia  # Si no se indica día, se copia el de la clase
        self.__hora: time = hora or clase.hora  # Si no se indica hora, se copia la de la clase

    @property
    def clase(self) -> Clase:  # Getter de la clase reservada
        return self.__clase  # Retorna el objeto Clase

    @property
    def dia(self) -> str:  # Getter del día reservado
        return self.__dia  # Retorna el día

    @property
    def hora(self) -> time:  # Getter de la hora reservada
        return self.__hora  # Retorna la hora

    @property
    def subtotal(self) -> int:  # Precio que aporta esta línea al total de la inscripción
        return self.__clase.precio_mensual  # El precio mensual de la clase reservada

    def resumen(self) -> str:  # Método del UML: descripción corta del detalle
        return f"{self.__clase.tipo} · {self.__dia} {self.__hora:%H:%M}"  # Ej: "Yoga · lunes 09:00"

    def __str__(self) -> str:  # Representación en texto
        return self.resumen()  # Reutiliza resumen()
