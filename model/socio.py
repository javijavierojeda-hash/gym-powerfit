"""
Clase Socio: el cliente del gimnasio.

Se registra con su RUT, que se valida ANTES de crear la ficha (requerimiento 3),
y se compone de una Membresia (rombo relleno en el UML: la membresía nace y
muere con el socio).
"""

from datetime import date, timedelta  # Importa fecha y diferencia de tiempo
from model.membresia import Membresia  # Importa la clase Membresia (parte de la composición)
from model.membresia_vencida_exception import MembresiaVencidaException  # Importa la excepción de ingreso
from model.validaciones import es_rut_valido, limpiar_rut, formatear_rut  # Importa las utilidades de RUT


class Socio:  # Define la clase Socio
    """
    Representa a un cliente del gimnasio con su membresía.
    """

    def __init__(  # Constructor del socio
        self,
        rut: str,  # RUT en cualquier formato (con o sin puntos)
        nombre: str,  # Nombre completo del socio
        fecha_inicio: date | None = None,  # Inicio de la membresía (opcional)
        fecha_vencimiento: date | None = None,  # Vencimiento de la membresía (opcional)
    ) -> None:
        if not Socio.validar_rut(rut):  # Valida el RUT antes de crear cualquier cosa
            raise ValueError(f"RUT invalido: {rut}")  # Si es inválido la ficha NO se crea
        if not nombre or not nombre.strip():  # Valida que el nombre no venga vacío
            raise ValueError("El nombre del socio es obligatorio")  # Rechaza nombres vacíos
        self.__rut: str = limpiar_rut(rut)  # Guarda el RUT normalizado (12345678-5)
        self.__nombre: str = nombre.strip()  # Guarda el nombre sin espacios sobrantes
        hoy = date.today()  # Obtiene la fecha actual
        inicio = fecha_inicio or hoy  # Si no se indica inicio, la membresía parte hoy
        vencimiento = fecha_vencimiento or (inicio - timedelta(days=1))  # Sin fecha: queda "sin pagar" (vencida)
        self.__membresia: Membresia = Membresia(inicio, vencimiento)  # COMPOSICIÓN: el socio crea su propia membresía

    @staticmethod
    def validar_rut(rut: str) -> bool:  # Método del UML: verifica que el RUT esté bien formado
        """
        Retorna True si el RUT es válido según el algoritmo módulo 11.
        Es estático porque no necesita un socio creado para usarse.
        """
        return es_rut_valido(rut)  # Delega en la función compartida de validaciones

    @property
    def rut(self) -> str:  # Getter de solo lectura del RUT (el RUT no se puede cambiar)
        return self.__rut  # Retorna el RUT normalizado

    @property
    def rut_formateado(self) -> str:  # RUT listo para mostrar en pantalla
        return formatear_rut(self.__rut)  # Ej: 12.345.678-5

    @property
    def nombre(self) -> str:  # Getter del nombre
        return self.__nombre  # Retorna el nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:  # Setter con validación del nombre
        if not valor or not valor.strip():  # No se permite dejar el nombre vacío
            raise ValueError("El nombre del socio es obligatorio")  # Rechaza el cambio
        self.__nombre = valor.strip()  # Actualiza el nombre limpio

    @property
    def membresia(self) -> Membresia:  # Getter de la membresía (la parte de la composición)
        return self.__membresia  # Retorna el objeto Membresia

    def puede_ingresar(self, hoy: date | None = None) -> bool:  # Método del UML: controla el ingreso al gimnasio
        """
        Retorna True si la membresía está vigente.
        Si está vencida LANZA MembresiaVencidaException (requerimiento 5).
        """
        if not self.__membresia.esta_vigente(hoy):  # Si la membresía no está vigente...
            raise MembresiaVencidaException(self)  # ...se detiene el ingreso con la excepción propia
        return True  # Si está vigente, puede ingresar

    def __str__(self) -> str:  # Representación en texto del socio
        return f"{self.__nombre} ({self.rut_formateado})"  # Ej: "Ana Perez (12.345.678-5)"
