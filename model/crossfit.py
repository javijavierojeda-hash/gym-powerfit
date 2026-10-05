"""
Clase Crossfit: hereda de Clase.
Regla de cupos: se reservan 2 cupos fijos para clases de prueba de socios
nuevos, por lo que la inscripción mensual solo puede usar 10 de los 12.
"""

from __future__ import annotations  # Permite usar anotaciones modernas (str | None) también en Python 3.7 a 3.9

from datetime import time  # Importa el tipo hora para el constructor
from model.clase import Clase  # Importa la clase base abstracta


class Crossfit(Clase):  # Crossfit ES UNA Clase (herencia)
    """
    Clase de Crossfit: 12 cupos (2 reservados), 50 minutos, $22.000 mensuales.
    """

    NOMBRE = "Crossfit"  # Nombre del tipo
    CUPO_MAXIMO = 12  # Cupo total del box
    DURACION_MIN = 50  # Dura 50 minutos
    PRECIO_MENSUAL = 22000  # Precio mensual en pesos
    CUPOS_RESERVADOS = 2  # Cupos guardados para clases de prueba (no se venden en la mensualidad)

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
        return max(self.CUPO_MAXIMO - self.CUPOS_RESERVADOS - self.inscritos, 0)  # Descuenta los cupos reservados
