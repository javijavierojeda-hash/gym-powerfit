"""
Clase InscripcionMensual: la inscripción de un socio para un mes.

Es la TRANSACCIÓN del modelo: agrupa todas las clases que el socio reservó ese
mes (requerimiento 4) y no permite reservar una clase llena (requerimiento 5).
"""

import re  # Importa expresiones regulares para validar el formato del mes
from datetime import date  # Importa el tipo fecha
from model.socio import Socio  # Importa Socio (asociación "genera")
from model.detalle_clase_reservada import DetalleClaseReservada  # Importa el detalle (composición "agrupa")

_PATRON_MES = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")  # Formato válido del mes: AAAA-MM (ej: 2026-10)


class InscripcionMensual:  # Define la clase de la inscripción mensual
    """
    Agrupa 1..* DetalleClaseReservada de un socio para un mes.
    """

    def __init__(  # Constructor de la inscripción
        self,
        socio: Socio,  # Socio que se inscribe
        mes: str,  # Mes en formato AAAA-MM
        fecha: date | None = None,  # Fecha en que se hizo la inscripción
        id: int | None = None,  # Id en la base de datos
        pagada: bool = False,  # Si la mensualidad ya fue cobrada
    ) -> None:
        if not isinstance(socio, Socio):  # Valida que se reciba un socio real
            raise TypeError("La inscripcion necesita un Socio")  # Rechaza datos inválidos
        if not _PATRON_MES.match(mes or ""):  # Valida el formato del mes
            raise ValueError("El mes debe tener formato AAAA-MM")  # Rechaza meses mal escritos
        self.__id: int | None = id  # Atributo privado: id en la base de datos
        self.__socio: Socio = socio  # Atributo privado: socio inscrito
        self.__mes: str = mes  # Atributo privado: mes de la inscripción
        self.__fecha: date = fecha or date.today()  # Atributo privado: fecha de la inscripción (hoy por defecto)
        self.__pagada: bool = pagada  # Atributo privado: estado del pago
        self.__detalles: list[DetalleClaseReservada] = []  # COMPOSICIÓN: lista privada de detalles

    # ---------- Propiedades ----------

    @property
    def id(self) -> int | None:  # Getter del id
        return self.__id  # Retorna el id

    @id.setter
    def id(self, valor: int) -> None:  # Setter del id (lo usa el DAO al guardar)
        if self.__id is not None:  # Si ya tenía id...
            raise ValueError("El id de la inscripcion no se puede modificar")  # ...no se permite cambiarlo
        self.__id = valor  # Asigna el id generado por la base de datos

    @property
    def socio(self) -> Socio:  # Getter del socio
        return self.__socio  # Retorna el socio

    @property
    def mes(self) -> str:  # Getter del mes
        return self.__mes  # Retorna el mes AAAA-MM

    @property
    def fecha(self) -> date:  # Getter de la fecha de inscripción
        return self.__fecha  # Retorna la fecha

    @property
    def pagada(self) -> bool:  # Getter del estado de pago
        return self.__pagada  # Retorna True si ya se pagó

    @property
    def detalles(self) -> tuple[DetalleClaseReservada, ...]:  # Getter de los detalles
        return tuple(self.__detalles)  # Retorna una TUPLA (copia inmutable): nadie puede alterar la lista desde afuera

    # ---------- Reglas de negocio ----------

    def agregar_clase(self, detalle: DetalleClaseReservada) -> None:  # Método del UML
        """
        Agrega una clase reservada a la inscripción.
        - Si la clase ya está en la inscripción, lanza ValueError.
        - Si la clase está llena, LANZA CupoLlenoException y no agrega nada.
        """
        if self.__pagada:  # Una inscripción ya pagada no se modifica
            raise ValueError("La inscripcion ya fue pagada y no se puede modificar")  # Protege la integridad del cobro
        if any(d.clase.id is not None and d.clase.id == detalle.clase.id for d in self.__detalles):  # Revisa duplicados por id
            raise ValueError(f"La clase {detalle.clase} ya esta en la inscripcion")  # No se reserva dos veces lo mismo
        if any(d.clase is detalle.clase for d in self.__detalles):  # Revisa duplicados por objeto (clases aún sin id)
            raise ValueError(f"La clase {detalle.clase} ya esta en la inscripcion")  # No se reserva dos veces lo mismo
        detalle.clase.registrar_inscrito()  # Suma el inscrito; si está llena lanza CupoLlenoException y se corta aquí
        self.__detalles.append(detalle)  # Solo si hubo cupo, el detalle queda en la inscripción

    def cargar_detalle(self, detalle: DetalleClaseReservada) -> None:  # Uso interno del DAO al leer desde la BD
        """
        Agrega un detalle YA guardado en la base de datos, sin volver a
        contar el cupo (ese inscrito ya está contado).
        """
        self.__detalles.append(detalle)  # Reconstruye la inscripción tal como está guardada

    def calcular_total(self) -> int:  # Método del UML: total a pagar del mes
        return sum(detalle.subtotal for detalle in self.__detalles)  # Suma el precio de cada clase reservada

    def marcar_pagada(self) -> None:  # Registra que la mensualidad fue cobrada
        if not self.__detalles:  # Regla 1..* del UML: no se cobra una inscripción vacía
            raise ValueError("La inscripcion debe tener al menos una clase reservada")  # Rechaza el cobro
        self.__pagada = True  # Marca la inscripción como pagada

    def __str__(self) -> str:  # Representación en texto
        return f"Inscripcion {self.__mes} de {self.__socio.nombre} ({len(self.__detalles)} clases)"  # Resumen corto
