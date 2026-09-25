"""
Clase Spinning: hereda de Clase.
Regla de cupos: depende de las bicicletas que estén operativas.
Si una bicicleta está en mantención, ese cupo desaparece.
"""

from datetime import time  # Importa el tipo hora para el constructor
from model.clase import Clase  # Importa la clase base abstracta


class Spinning(Clase):  # Spinning ES UNA Clase (herencia)
    """
    Clase de Spinning: 15 bicicletas, 45 minutos, $18.000 mensuales.
    """

    NOMBRE = "Spinning"  # Nombre del tipo
    CUPO_MAXIMO = 15  # Hay 15 bicicletas en la sala
    DURACION_MIN = 45  # Dura 45 minutos
    PRECIO_MENSUAL = 18000  # Precio mensual en pesos

    def __init__(  # Constructor propio: agrega las bicicletas operativas
        self,
        dia: str,  # Día de la semana
        hora: time,  # Hora de inicio
        instructor_rut: str | None = None,  # RUT del instructor
        id: int | None = None,  # Id en la base de datos
        inscritos: int = 0,  # Inscritos del mes
        bicicletas_operativas: int | None = None,  # Bicicletas que funcionan (por defecto todas)
    ) -> None:
        super().__init__(dia, hora, instructor_rut, id, inscritos)  # Inicializa la parte común con el constructor del padre
        self.__bicicletas_operativas: int = self.CUPO_MAXIMO  # Valor inicial: todas las bicicletas funcionan
        if bicicletas_operativas is not None:  # Si se indicó otra cantidad...
            self.bicicletas_operativas = bicicletas_operativas  # ...se asigna usando el setter que valida

    @property
    def bicicletas_operativas(self) -> int:  # Getter de bicicletas operativas
        return self.__bicicletas_operativas  # Retorna cuántas bicicletas funcionan

    @bicicletas_operativas.setter
    def bicicletas_operativas(self, valor: int) -> None:  # Setter con validación
        if not isinstance(valor, int) or not 0 <= valor <= self.CUPO_MAXIMO:  # Debe estar entre 0 y 15
            raise ValueError(f"Las bicicletas operativas deben estar entre 0 y {self.CUPO_MAXIMO}")  # Rechaza el valor
        self.__bicicletas_operativas = valor  # Guarda la cantidad válida

    def cupos_disponibles(self) -> int:  # Sobrescribe el método abstracto de Clase
        return max(self.__bicicletas_operativas - self.inscritos, 0)  # Solo cuentan las bicicletas que funcionan
