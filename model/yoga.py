"""
Clase Yoga: hereda de Clase.
Regla de cupos: la más simple, cupo máximo menos inscritos.
"""

from __future__ import annotations  # Permite usar anotaciones modernas (str | None) también en Python 3.7 a 3.9

from datetime import time  # Importa el tipo hora para el constructor
from model.clase import Clase  # Importa la clase base abstracta


class Yoga(Clase):  # Yoga ES UNA Clase (herencia)
    """
    Clase de Yoga: 20 cupos, 60 minutos, $15.000 mensuales.
    """

    NOMBRE = "Yoga"  # Nombre del tipo
    CUPO_MAXIMO = 20  # Caben 20 colchonetas en la sala
    DURACION_MIN = 60  # Dura una hora
    PRECIO_MENSUAL = 15000  # Precio mensual en pesos

    def __init__(  # Constructor propio del subtipo
        self,
        dia: str,  # Día de la semana
        hora: time,  # Hora de inicio
        instructor_rut: str | None = None,  # RUT del instructor
        id: int | None = None,  # Id en la base de datos
        inscritos: int = 0,  # Inscritos del mes
    ) -> None:
        super().__init__(dia, hora, instructor_rut, id, inscritos)  # Llama al constructor de la clase base Clase

    def cupos_disponibles(self) -> int:  # Sobrescribe el método abstracto de Clase
        return max(self.CUPO_MAXIMO - self.inscritos, 0)  # Cupo menos inscritos (nunca negativo)
