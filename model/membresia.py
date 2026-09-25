"""
Clase Membresia: la afiliación de un socio al gimnasio.

Se separa de Socio para mantener la lógica del vencimiento en un solo lugar.
En el UML es una composición: la membresía existe solo dentro de su socio.
"""

from datetime import date, timedelta  # Importa fecha (sin hora) y diferencia de tiempo de la librería estándar

_UN_DIA = timedelta(days=1)  # Constante privada: un día (permite membresías "sin pagar" que vencen el día anterior al inicio)


class Membresia:  # Define la clase Membresia
    """
    Representa el período en que un socio puede usar el gimnasio.
    """

    VIGENTE = "vigente"  # Constante para el estado vigente (evita errores de tipeo)
    VENCIDA = "vencida"  # Constante para el estado vencido

    def __init__(self, fecha_inicio: date, fecha_vencimiento: date) -> None:  # Constructor con las dos fechas
        if fecha_vencimiento < fecha_inicio - _UN_DIA:  # Valida que el vencimiento no sea absurdo (muy anterior al inicio)
            raise ValueError("La fecha de vencimiento no puede ser anterior al inicio")  # Rechaza datos inconsistentes
        self.__fecha_inicio: date = fecha_inicio  # Atributo privado: fecha en que comenzó la membresía
        self.__fecha_vencimiento: date = fecha_vencimiento  # Atributo privado: último día en que es válida

    @property
    def fecha_inicio(self) -> date:  # Getter de solo lectura para la fecha de inicio
        return self.__fecha_inicio  # Retorna la fecha de inicio

    @property
    def fecha_vencimiento(self) -> date:  # Getter de solo lectura para la fecha de vencimiento
        return self.__fecha_vencimiento  # Retorna la fecha de vencimiento

    @property
    def estado(self) -> str:  # El estado se calcula siempre, así nunca queda desactualizado
        return self.VIGENTE if self.esta_vigente() else self.VENCIDA  # Depende de si hoy está dentro del período

    def esta_vigente(self, hoy: date | None = None) -> bool:  # Indica si la membresía sirve en la fecha dada
        """
        Retorna True si la fecha de hoy es menor o igual al vencimiento.
        El parámetro 'hoy' permite probar el método con fechas fijas.
        """
        hoy = hoy or date.today()  # Si no se entrega fecha, usa la fecha actual del sistema
        return self.__fecha_inicio <= hoy <= self.__fecha_vencimiento  # Vigente si hoy está dentro del rango

    def dias_restantes(self, hoy: date | None = None) -> int:  # Calcula cuántos días le quedan a la membresía
        """
        Retorna los días que faltan para el vencimiento (0 si ya venció).
        """
        hoy = hoy or date.today()  # Usa la fecha actual si no se entrega una
        return max((self.__fecha_vencimiento - hoy).days, 0)  # Diferencia en días, nunca negativa

    def renovar_hasta(self, nueva_fecha: date, hoy: date | None = None) -> None:  # Extiende la membresía al pagar
        """
        Extiende la membresía hasta 'nueva_fecha'. Si estaba vencida,
        el nuevo período comienza hoy.
        """
        hoy = hoy or date.today()  # Usa la fecha actual si no se entrega una
        if nueva_fecha < hoy:  # No tiene sentido renovar hacia una fecha pasada
            raise ValueError("No se puede renovar hacia una fecha pasada")  # Rechaza la operación
        if not self.esta_vigente(hoy):  # Si la membresía estaba vencida o sin pagar...
            self.__fecha_inicio = hoy  # ...el nuevo período parte hoy
        self.__fecha_vencimiento = max(self.__fecha_vencimiento, nueva_fecha)  # Nunca acorta una membresía ya pagada

    def __str__(self) -> str:  # Representación en texto de la membresía
        return f"Membresia {self.estado} hasta {self.__fecha_vencimiento:%d-%m-%Y}"  # Ej: "Membresia vigente hasta 31-10-2026"

