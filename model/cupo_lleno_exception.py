"""
Excepción propia del dominio: se lanza al intentar reservar una clase sin cupos.
Corresponde a <<exception>> CupoLlenoException del diagrama UML.
"""


class CupoLlenoException(Exception):  # Hereda de Exception: es una excepción propia del negocio
    """
    Se lanza cuando se intenta agregar una clase cuyo cupo ya está completo.
    Detiene la operación en lugar de permitirla en silencio.
    """

    MENSAJE = "La clase ya alcanzo su cupo maximo"  # Mensaje por defecto definido en el UML

    def __init__(self, clase) -> None:  # Constructor que recibe la clase que está llena
        self.mensaje: str = self.MENSAJE  # Guarda el mensaje por defecto como atributo
        self.clase = clase  # Guarda la clase que provocó el error, para informar cuál fue
        super().__init__(str(self))  # Inicializa la Exception base con el texto completo

    def __str__(self) -> str:  # Define cómo se muestra la excepción como texto
        return f"{self.mensaje}: {self.clase}"  # Ej: "La clase ya alcanzo su cupo maximo: Yoga lunes 09:00"
