"""
Clase abstracta Clase: cualquier clase del gimnasio (Yoga, Spinning o Crossfit).

Guarda lo común (horario, duración, cupo, inscritos) y obliga a cada tipo
a definir su propia regla de cupos con el método abstracto cupos_disponibles().
Esto es POLIMORFISMO: el mismo mensaje da resultados distintos según el tipo.
"""

from abc import ABC, abstractmethod  # Importa lo necesario para crear clases abstractas
from datetime import time  # Importa el tipo hora (sin fecha)
from model.cupo_lleno_exception import CupoLlenoException  # Importa la excepción de cupo lleno

DIAS_SEMANA = ("lunes", "martes", "miercoles", "jueves", "viernes", "sabado", "domingo")  # Días válidos para programar clases


class Clase(ABC):  # Hereda de ABC: no se puede instanciar directamente
    """
    Base de los tres tipos de clase. Cada subclase define como constantes
    su NOMBRE, CUPO_MAXIMO, DURACION_MIN y PRECIO_MENSUAL.
    """

    NOMBRE: str = "Clase"  # Nombre del tipo de clase (cada subclase lo reemplaza)
    CUPO_MAXIMO: int = 0  # Cupo máximo del tipo (cada subclase lo reemplaza)
    DURACION_MIN: int = 0  # Duración en minutos (cada subclase lo reemplaza)
    PRECIO_MENSUAL: int = 0  # Precio mensual en pesos por asistir a esta clase (cada subclase lo reemplaza)

    def __init__(  # Constructor común a todas las clases
        self,
        dia: str,  # Día de la semana en que se dicta (ej: "lunes")
        hora: time,  # Hora de inicio
        instructor_rut: str | None = None,  # RUT del instructor que la dicta (asociación del UML)
        id: int | None = None,  # Identificador en la base de datos (None si aún no se guarda)
        inscritos: int = 0,  # Socios ya inscritos este mes
    ) -> None:
        dia = (dia or "").strip().lower()  # Normaliza el día a minúsculas y sin espacios
        if dia not in DIAS_SEMANA:  # Valida que sea un día real de la semana
            raise ValueError(f"Dia invalido: {dia}")  # Rechaza días inexistentes
        if not isinstance(hora, time):  # Valida que la hora sea un objeto time
            raise TypeError("La hora debe ser un objeto datetime.time")  # Evita guardar texto como hora
        self.__id: int | None = id  # Atributo privado: id de la base de datos
        self.__dia: str = dia  # Atributo privado: día de la semana
        self.__hora: time = hora  # Atributo privado: hora de inicio
        self.__instructor_rut: str | None = instructor_rut  # Atributo privado: RUT del instructor
        self.__inscritos: int = 0  # Se inicia en 0 y luego se asigna con el setter (que valida)
        self.inscritos = inscritos  # Usa el setter para validar el valor recibido

    # ---------- Propiedades (encapsulamiento) ----------

    @property
    def id(self) -> int | None:  # Getter del id
        return self.__id  # Retorna el id (o None si no se ha guardado)

    @id.setter
    def id(self, valor: int) -> None:  # Setter del id: lo usa el DAO después de insertar
        if self.__id is not None:  # Si la clase ya tenía id...
            raise ValueError("El id de la clase no se puede modificar")  # ...no se permite cambiarlo
        self.__id = valor  # Asigna el id generado por la base de datos

    @property
    def tipo(self) -> str:  # Nombre del tipo de clase (Yoga, Spinning, Crossfit)
        return self.NOMBRE  # Retorna la constante definida por la subclase

    @property
    def dia(self) -> str:  # Getter del día
        return self.__dia  # Retorna el día de la semana

    @property
    def hora(self) -> time:  # Getter de la hora
        return self.__hora  # Retorna la hora de inicio

    @property
    def horario(self) -> str:  # Atributo "horario" del UML, en formato legible
        return f"{self.__dia} {self.__hora:%H:%M}"  # Ej: "lunes 09:00"

    @property
    def duracion_min(self) -> int:  # Duración de la clase en minutos
        return self.DURACION_MIN  # Cada tipo tiene la suya

    @property
    def cupo_maximo(self) -> int:  # Cupo máximo del tipo de clase
        return self.CUPO_MAXIMO  # Cada tipo tiene el suyo

    @property
    def precio_mensual(self) -> int:  # Precio mensual de la clase
        return self.PRECIO_MENSUAL  # Cada tipo tiene el suyo

    @property
    def instructor_rut(self) -> str | None:  # Getter del instructor asignado
        return self.__instructor_rut  # Retorna el RUT del instructor

    @instructor_rut.setter
    def instructor_rut(self, rut: str) -> None:  # Setter del instructor
        self.__instructor_rut = rut  # Asigna el instructor que dicta la clase

    @property
    def inscritos(self) -> int:  # Getter de la cantidad de inscritos
        return self.__inscritos  # Retorna cuántos socios hay inscritos

    @inscritos.setter
    def inscritos(self, valor: int) -> None:  # Setter con validación de inscritos
        if not isinstance(valor, int) or valor < 0:  # No se aceptan valores negativos ni no enteros
            raise ValueError("Los inscritos deben ser un entero mayor o igual a 0")  # Rechaza el valor
        self.__inscritos = valor  # Guarda el valor válido

    # ---------- Reglas de negocio ----------

    @abstractmethod
    def cupos_disponibles(self) -> int:  # Método ABSTRACTO del UML: cada tipo calcula distinto
        """
        Retorna cuántos socios más pueden inscribirse.
        Cada subclase DEBE implementarlo con su propia regla.
        """

    def esta_llena(self) -> bool:  # Método del UML: apoyo a la regla de cupo
        return self.cupos_disponibles() <= 0  # Está llena si no quedan cupos

    def registrar_inscrito(self) -> None:  # Suma un inscrito respetando el cupo
        """
        Agrega un inscrito. Si la clase está llena LANZA CupoLlenoException.
        """
        if self.esta_llena():  # Antes de sumar, revisa si queda cupo
            raise CupoLlenoException(self)  # Detiene la operación con la excepción propia
        self.__inscritos += 1  # Si hay cupo, suma un inscrito

    def liberar_cupo(self) -> None:  # Resta un inscrito (por ejemplo, al anular una reserva)
        if self.__inscritos > 0:  # Solo resta si hay alguien inscrito
            self.__inscritos -= 1  # Libera un cupo

    def __str__(self) -> str:  # Representación en texto de la clase
        return f"{self.tipo} {self.horario}"  # Ej: "Yoga lunes 09:00"
