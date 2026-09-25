from datetime import date, time  # Importa fecha y hora para convertir datos de la BD
from dao.dao import Dao  # Importa la clase base Dao
from dao.clase_dao import ClaseDao  # Importa ClaseDao para revisar cupos contra la BD
from dao.socio_dao import SocioDao  # Importa SocioDao para reconstruir al socio
from dao.membresia_dao import MembresiaDao  # Importa MembresiaDao para guardar la renovación al pagar
from dao.detalle_clase_reservada_dao import DetalleClaseReservadaDao  # Importa el DAO de los detalles
from model.inscripcion_mensual import InscripcionMensual  # Importa la clase del modelo
from model.detalle_clase_reservada import DetalleClaseReservada  # Importa el detalle del modelo
from model.cupo_lleno_exception import CupoLlenoException  # Importa la excepción de cupo lleno


class InscripcionMensualDao(Dao):  # Define la clase InscripcionMensualDao que hereda de Dao
    """
    Data Access Object para la entidad InscripcionMensual (la transacción del negocio).

    guardar() vuelve a revisar el cupo de cada clase CONTRA LA BASE DE DATOS
    dentro de una transacción con BEGIN IMMEDIATE. Así, aunque dos
    recepcionistas inscriban al mismo tiempo, nunca se supera el cupo.
    """

    def crear_tabla(self):  # Define el método para crear la tabla de inscripciones
        """
        Crea la tabla 'inscripciones_mensuales' si no existe:
        - id: INTEGER PRIMARY KEY AUTOINCREMENT
        - socio_rut: TEXT NOT NULL (FK a socios) -> asociación "genera"
        - mes: TEXT NOT NULL (AAAA-MM)
        - fecha: TEXT NOT NULL (fecha de inscripción)
        - pagada: INTEGER (0/1), monto_pagado, fecha_pago
        - recepcionista_rut: TEXT (FK a recepcionistas) -> asociación "registra"
        - UNIQUE(socio_rut, mes): una sola inscripción por socio y mes
        """
        sql = """
        CREATE TABLE IF NOT EXISTS inscripciones_mensuales(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            socio_rut TEXT NOT NULL,
            mes TEXT NOT NULL,
            fecha TEXT NOT NULL,
            pagada INTEGER NOT NULL DEFAULT 0,
            monto_pagado INTEGER,
            fecha_pago TEXT,
            recepcionista_rut TEXT,
            UNIQUE (socio_rut, mes),
            FOREIGN KEY (socio_rut) REFERENCES socios (rut) ON DELETE CASCADE,
            FOREIGN KEY (recepcionista_rut) REFERENCES recepcionistas (rut) ON DELETE SET NULL
        )
        """
        self.cursor.execute(sql)  # Ejecuta la consulta SQL para crear la tabla
        self.conexion.commit()  # Confirma los cambios en la base de datos

    # ---------- Escritura ----------

    def guardar(self, inscripcion: InscripcionMensual, recepcionista_rut: str | None = None) -> int:  # Guarda una inscripción nueva
        """
        Guarda la inscripción con todos sus detalles en UNA transacción.
        - Si el socio ya tiene inscripción ese mes -> ValueError.
        - Si no tiene clases -> ValueError (regla 1..* del UML).
        - Si alguna clase está llena según la BD -> CupoLlenoException y
          se deshace todo (rollback): no queda una inscripción a medias.
        """
        if not inscripcion.detalles:  # Regla 1..*: al menos una clase reservada
            raise ValueError("La inscripcion debe tener al menos una clase reservada")  # Rechaza inscripciones vacías
        clase_dao = ClaseDao(self.conexion)  # DAO para releer las clases con sus inscritos reales
        detalle_dao = DetalleClaseReservadaDao(self.conexion)  # DAO para guardar cada detalle
        with self.transaccion():  # BEGIN IMMEDIATE: nadie más puede escribir hasta el commit
            if self.buscar_id(inscripcion.socio.rut, inscripcion.mes) is not None:  # Revisa si ya existe una inscripción ese mes
                raise ValueError(f"{inscripcion.socio.nombre} ya tiene inscripcion para {inscripcion.mes}")  # Rechaza el duplicado
            for detalle in inscripcion.detalles:  # Revisa el cupo de cada clase reservada
                clase_bd = clase_dao.buscar_por_id(detalle.clase.id, inscripcion.mes)  # Relee la clase con los inscritos guardados
                if clase_bd is None:  # Si la clase ya no existe...
                    raise ValueError(f"La clase {detalle.clase} ya no existe")  # ...se rechaza
                if clase_bd.esta_llena():  # Si según la BD ya no quedan cupos...
                    raise CupoLlenoException(clase_bd)  # ...se lanza la excepción y la transacción hace rollback
            self.cursor.execute(  # Inserta la cabecera de la inscripción
                """INSERT INTO inscripciones_mensuales(socio_rut, mes, fecha, pagada, recepcionista_rut)
                   VALUES (?, ?, ?, ?, ?)""",  # Consulta parametrizada
                (inscripcion.socio.rut, inscripcion.mes, inscripcion.fecha.isoformat(),  # Socio, mes y fecha
                 int(inscripcion.pagada), recepcionista_rut),  # Estado de pago y quién la registró
            )
            inscripcion.id = self.cursor.lastrowid  # Asigna al objeto el id generado
            for detalle in inscripcion.detalles:  # Recorre las clases reservadas
                detalle_dao.insertar(inscripcion.id, detalle)  # Guarda cada detalle en la MISMA transacción
        return inscripcion.id  # Retorna el id de la inscripción

    def registrar_pago(self, inscripcion: InscripcionMensual, monto: int, recepcionista_rut: str | None = None) -> None:  # Guarda el cobro
        """
        Marca la inscripción como pagada y guarda la membresía renovada del
        socio, ambas cosas en UNA transacción.
        """
        with self.transaccion():  # Todo o nada
            self.cursor.execute(  # Actualiza el estado de pago
                """UPDATE inscripciones_mensuales
                   SET pagada = 1, monto_pagado = ?, fecha_pago = ?, recepcionista_rut = COALESCE(?, recepcionista_rut)
                   WHERE id = ? AND pagada = 0""",  # "AND pagada = 0" impide registrar dos veces el mismo pago
                (monto, date.today().isoformat(), recepcionista_rut, inscripcion.id),  # Monto, fecha de hoy, cajero e id
            )
            if self.cursor.rowcount != 1:  # Si no se actualizó exactamente una fila...
                raise ValueError("La inscripcion no existe o ya estaba pagada")  # ...se cancela todo
            MembresiaDao(self.conexion).actualizar(inscripcion.socio)  # Guarda la membresía extendida del socio

    def eliminar(self, inscripcion_id: int) -> None:  # Anula una inscripción NO pagada
        with self.transaccion():  # Abre una transacción
            self.cursor.execute(  # Borra la inscripción (los detalles se borran en cascada)
                "DELETE FROM inscripciones_mensuales WHERE id = ? AND pagada = 0",  # Nunca se borra una inscripción pagada
                (inscripcion_id,),  # Id de la inscripción
            )
            if self.cursor.rowcount != 1:  # Si no se borró nada...
                raise ValueError("Solo se pueden anular inscripciones existentes y no pagadas")  # ...se informa

    # ---------- Lectura ----------

    def buscar_id(self, socio_rut: str, mes: str) -> int | None:  # Busca solo el id de la inscripción de un socio en un mes
        fila = self.cursor.execute(  # Ejecuta la consulta
            "SELECT id FROM inscripciones_mensuales WHERE socio_rut = ? AND mes = ?",  # Parametrizada
            (socio_rut, mes),  # RUT y mes
        ).fetchone()  # Toma la primera fila
        return fila["id"] if fila else None  # Retorna el id o None

    def buscar(self, socio_rut: str, mes: str) -> InscripcionMensual | None:  # Reconstruye la inscripción completa
        id_ = self.buscar_id(socio_rut, mes)  # Busca el id
        return self.buscar_por_id(id_) if id_ is not None else None  # Si existe, la reconstruye

    def buscar_por_id(self, inscripcion_id: int) -> InscripcionMensual | None:  # Reconstruye una inscripción por su id
        fila = self.cursor.execute(  # Lee la cabecera
            "SELECT * FROM inscripciones_mensuales WHERE id = ?", (inscripcion_id,)  # Consulta parametrizada
        ).fetchone()  # Toma la fila
        if fila is None:  # Si no existe...
            return None  # ...retorna None
        socio = SocioDao(self.conexion).buscar_por_rut(fila["socio_rut"])  # Reconstruye al socio con su membresía
        inscripcion = InscripcionMensual(  # Crea el objeto del modelo
            socio, fila["mes"], date.fromisoformat(fila["fecha"]),  # Socio, mes y fecha
            id=fila["id"], pagada=bool(fila["pagada"]),  # Id y estado de pago
        )
        clase_dao = ClaseDao(self.conexion)  # DAO para leer cada clase
        for d in DetalleClaseReservadaDao(self.conexion).listar_por_inscripcion(inscripcion_id):  # Recorre los detalles guardados
            clase = clase_dao.buscar_por_id(d["clase_id"], fila["mes"])  # Lee la clase con los inscritos de ese mes
            inscripcion.cargar_detalle(DetalleClaseReservada(clase, d["dia"], time.fromisoformat(d["hora"])))  # Agrega el detalle sin recontar cupo
        return inscripcion  # Retorna la inscripción completa

    def listar(self, mes: str) -> list[InscripcionMensual]:  # Lista las inscripciones de un mes
        filas = self.cursor.execute(  # Obtiene los ids del mes
            "SELECT id FROM inscripciones_mensuales WHERE mes = ? ORDER BY fecha DESC, id DESC", (mes,)  # Más recientes primero
        ).fetchall()  # Lista de filas
        return [self.buscar_por_id(f["id"]) for f in filas]  # Reconstruye cada inscripción

    def listar_por_socio(self, socio_rut: str) -> list[InscripcionMensual]:  # Historial de inscripciones de un socio
        filas = self.cursor.execute(  # Obtiene los ids de sus inscripciones
            "SELECT id FROM inscripciones_mensuales WHERE socio_rut = ? ORDER BY mes DESC", (socio_rut,)  # Mes más reciente primero
        ).fetchall()  # Lista de filas
        return [self.buscar_por_id(f["id"]) for f in filas]  # Reconstruye cada inscripción

    def listar_socios_de_clase(self, clase_id: int, mes: str) -> list:  # Socios inscritos en una clase en un mes
        ruts = self.cursor.execute(  # Obtiene los RUT de los socios con reserva en esa clase
            """SELECT i.socio_rut FROM detalles_clase_reservada d
               JOIN inscripciones_mensuales i ON i.id = d.inscripcion_id
               WHERE d.clase_id = ? AND i.mes = ?""",  # Une detalles con su inscripción para filtrar por mes
            (clase_id, mes),  # Id de la clase y mes
        ).fetchall()  # Lista de filas
        socio_dao = SocioDao(self.conexion)  # DAO para reconstruir cada socio
        socios = [socio_dao.buscar_por_rut(f["socio_rut"]) for f in ruts]  # Reconstruye los socios
        return sorted(socios, key=lambda s: s.nombre)  # Los ordena por nombre
