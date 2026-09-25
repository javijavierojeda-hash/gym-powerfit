"""
Clase Crossfit: hereda de Clase.
Regla de cupos: se reservan 2 cupos fijos para clases de prueba de socios
nuevos, por lo que la inscripción mensual solo puede usar 10 de los 12.
"""

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

    def cupos_disponibles(self) -> int:  # Sobrescribe el método abstracto de Clase
        return max(self.CUPO_MAXIMO - self.CUPOS_RESERVADOS - self.inscritos, 0)  # Descuenta los cupos reservados
