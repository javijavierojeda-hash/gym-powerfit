"""
Clase Instructor: hereda de Trabajador.
Dicta las clases, marca la asistencia y es el único que puede crear clases.
"""

from datetime import time  # Importa el tipo hora
from model.trabajador import Trabajador  # Importa la clase base abstracta
from model.clase import Clase  # Importa Clase para los type hints
from model.socio import Socio  # Importa Socio para los type hints
from model.yoga import Yoga  # Importa los tres tipos de clase...
from model.spinning import Spinning  # ...para poder crearlas...
from model.crossfit import Crossfit  # ...desde crear_clase()

TIPOS_DE_CLASE = {"yoga": Yoga, "spinning": Spinning, "crossfit": Crossfit}  # Relaciona el nombre del tipo con su clase Python


class Instructor(Trabajador):  # Instructor ES UN Trabajador (herencia)
    """
    Trabajador a cargo de las clases y de registrar la asistencia.
    """

    @property
    def rol(self) -> str:  # Implementa la propiedad abstracta del padre
        return "instructor"  # Rol usado por el control de acceso de la web

    def crear_clase(self, tipo: str, dia: str, hora: time) -> Clase:  # Solo el instructor puede crear clases
        """
        Crea una clase del tipo indicado y la deja asignada a este instructor.
        La recepcionista NO tiene este método (requerimiento 2).
        """
        clase_python = TIPOS_DE_CLASE.get((tipo or "").lower())  # Busca la clase Python según el texto
        if clase_python is None:  # Si el tipo no existe...
            raise ValueError(f"Tipo de clase invalido: {tipo}")  # ...se rechaza
        return clase_python(dia, hora, instructor_rut=self.rut)  # Crea la clase asignada a este instructor

    def dictar_clase(self, c: Clase) -> None:  # Método del UML: el instructor toma la clase
        c.instructor_rut = self.rut  # Asocia la clase con este instructor (relación "dicta")

    def marcar_asistencia(self, c: Clase, s: Socio) -> None:  # Método del UML
        """
        Valida que se pueda registrar la asistencia de un socio a una clase.
        - Solo el instructor de la clase puede marcarla (PermissionError).
        - El socio debe tener la membresía vigente (MembresiaVencidaException).
        La persistencia (guardar en la BD) la hace AsistenciaDao.
        """
        if c.instructor_rut != self.rut:  # Revisa que la clase sea de este instructor
            raise PermissionError("Solo el instructor de la clase puede marcar asistencia")  # Bloquea a otros instructores
        s.puede_ingresar()  # Si la membresía está vencida, lanza MembresiaVencidaException
