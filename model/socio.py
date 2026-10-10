"""
Clase Socio: el cliente del gimnasio.

Se registra con su RUT, que se valida en el SETTER antes de crear la ficha (requerimiento 3),
y se compone de una Membresia (rombo relleno en el UML: la membresía nace y
muere con el socio). El correo y el teléfono son opcionales, pero si se
ingresan también se validan en sus setters.
"""

from __future__ import annotations  # Permite usar anotaciones modernas (str | None) también en Python 3.7 a 3.9

import re  # Expresiones regulares para validar el formato del correo
from datetime import date, timedelta  # Importa fecha y diferencia de tiempo
from model.membresia import Membresia  # Importa la clase Membresia (parte de la composición)
from model.membresia_vencida_exception import MembresiaVencidaException  # Importa la excepción de ingreso
from model.validaciones import es_rut_valido, limpiar_rut, formatear_rut  # Importa las utilidades de RUT

_PATRON_CORREO = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")  # algo@dominio.cl (sin espacios y con un solo @)


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
        correo: str = "",  # Correo de contacto (opcional)
        telefono: str = "",  # Teléfono celular (opcional)
    ) -> None:
        self.rut = rut  # Usa el SETTER: si el RUT es inválido lanza ValueError y la ficha NO se crea
        self.nombre = nombre  # Usa el setter del nombre (valida que no venga vacío)
        self.correo = correo  # Usa el setter del correo (valida el formato si viene)
        self.telefono = telefono  # Usa el setter del teléfono (valida el formato si viene)
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
    def rut(self) -> str:  # Getter del RUT
        return self.__rut  # Retorna el RUT normalizado

    @rut.setter
    def rut(self, valor: str) -> None:  # SETTER con validación: el dato que la ficha exige validar
        """
        Valida el RUT con el algoritmo módulo 11 antes de guardarlo.
        Igual que el setter de 'patente' del Vehiculo del profesor.
        """
        if not Socio.validar_rut(valor):  # Si el RUT no es válido...
            raise ValueError(f"RUT invalido: {valor}")  # ...se rechaza y el atributo no cambia
        self.__rut = limpiar_rut(valor)  # Guarda el RUT normalizado (12345678-5)

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
        if len(valor.strip()) > 80:  # Rango: un nombre de más de 80 caracteres no es real
            raise ValueError("El nombre no puede superar los 80 caracteres")  # Rechaza el cambio
        self.__nombre = valor.strip()  # Actualiza el nombre limpio

    @property
    def correo(self) -> str:  # Getter del correo
        return self.__correo  # Retorna el correo ("" si no tiene)

    @correo.setter
    def correo(self, valor: str) -> None:  # Setter con validación del correo
        texto = (valor or "").strip().lower()  # Limpia espacios y pasa a minúsculas
        if texto and (len(texto) > 100 or not _PATRON_CORREO.match(texto)):  # Si viene, debe tener formato de correo
            raise ValueError(f"Correo invalido: {valor} (ejemplo: nombre@correo.cl)")  # Rechaza el cambio
        self.__correo = texto  # Guarda el correo validado (o vacío)

    @property
    def telefono(self) -> str:  # Getter del teléfono
        return self.__telefono  # Retorna el teléfono de 9 dígitos ("" si no tiene)

    @telefono.setter
    def telefono(self, valor: str) -> None:  # Setter con validación del teléfono
        texto = re.sub(r"[\s-]", "", valor or "")  # Quita espacios y guiones
        if texto.startswith("+56"):  # Acepta el prefijo de Chile...
            texto = texto[3:]  # ...y lo quita para guardar solo el número
        if texto and not (len(texto) == 9 and texto.isdigit() and texto.startswith("9")):  # Celular chileno: 9 dígitos que parten en 9
            raise ValueError(f"Telefono invalido: {valor} (ejemplo: 912345678)")  # Rechaza el cambio
        self.__telefono = texto  # Guarda el teléfono validado (o vacío)

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
