"""
Excepción propia del dominio: se lanza al verificar el ingreso de un socio
cuya membresía no está vigente.
Corresponde a <<exception>> MembresiaVencidaException del diagrama UML.
"""


class MembresiaVencidaException(Exception):  # Hereda de Exception: excepción propia del negocio
    """
    Se lanza cuando un socio intenta ingresar al gimnasio con la membresía vencida.
    """

    MENSAJE = "La membresia del socio esta vencida"  # Mensaje por defecto definido en el UML

    def __init__(self, socio) -> None:  # Constructor que recibe el socio rechazado
        self.mensaje: str = self.MENSAJE  # Guarda el mensaje por defecto
        self.socio = socio  # Guarda el socio para saber a quién se le negó el ingreso
        self.fecha_vencimiento = socio.membresia.fecha_vencimiento  # Guarda la fecha en que venció su membresía
        super().__init__(str(self))  # Inicializa la Exception base con el texto completo

    def __str__(self) -> str:  # Define cómo se muestra la excepción como texto
        fecha = self.fecha_vencimiento.strftime("%d-%m-%Y")  # Da formato chileno a la fecha (día-mes-año)
        return f"{self.mensaje}: {self.socio.nombre} (vencio el {fecha})"  # Mensaje completo y claro
