"""
Clase Yoga: hereda de Clase.
Regla de cupos: la más simple, cupo máximo menos inscritos.
"""

from model.clase import Clase  # Importa la clase base abstracta


class Yoga(Clase):  # Yoga ES UNA Clase (herencia)
    """
    Clase de Yoga: 20 cupos, 60 minutos, $15.000 mensuales.
    """

    NOMBRE = "Yoga"  # Nombre del tipo
    CUPO_MAXIMO = 20  # Caben 20 colchonetas en la sala
    DURACION_MIN = 60  # Dura una hora
    PRECIO_MENSUAL = 15000  # Precio mensual en pesos

    def cupos_disponibles(self) -> int:  # Sobrescribe el método abstracto de Clase
        return max(self.CUPO_MAXIMO - self.inscritos, 0)  # Cupo menos inscritos (nunca negativo)
