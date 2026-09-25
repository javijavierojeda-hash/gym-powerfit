from dao.dao import Dao  # Importa la clase base Dao


class MembresiaDao(Dao):  # Define la clase MembresiaDao que hereda de Dao
    """
    Data Access Object para la entidad Membresia.

    La composición Socio ◆── Membresia (1 a 1) se implementa con:
    - socio_rut UNIQUE: un socio no puede tener dos membresías.
    - ON DELETE CASCADE: si se borra el socio, su membresía desaparece con él.
    """

    def crear_tabla(self):  # Define el método para crear la tabla de membresías
        """
        Crea la tabla 'membresias' si no existe:
        - id: INTEGER PRIMARY KEY AUTOINCREMENT
        - socio_rut: TEXT NOT NULL UNIQUE (FK hacia socios.rut)
        - fecha_inicio, fecha_vencimiento: TEXT (formato ISO AAAA-MM-DD)
        - estado: TEXT (vigente / vencida, al momento de guardar)
        """
        sql = """
        CREATE TABLE IF NOT EXISTS membresias(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            socio_rut TEXT NOT NULL UNIQUE,
            fecha_inicio TEXT NOT NULL,
            fecha_vencimiento TEXT NOT NULL,
            estado TEXT NOT NULL,
            FOREIGN KEY (socio_rut) REFERENCES socios (rut) ON DELETE CASCADE
        )
        """
        self.cursor.execute(sql)  # Ejecuta la consulta SQL para crear la tabla
        self.conexion.commit()  # Confirma los cambios en la base de datos

    def insertar(self, socio) -> None:  # Guarda la membresía de un socio
        m = socio.membresia  # Obtiene la membresía del socio (la parte de la composición)
        with self.transaccion():  # Abre (o se une a) una transacción
            self.cursor.execute(  # Inserta la fila
                """INSERT INTO membresias(socio_rut, fecha_inicio, fecha_vencimiento, estado)
                   VALUES (?, ?, ?, ?)""",  # Consulta parametrizada
                (socio.rut, m.fecha_inicio.isoformat(), m.fecha_vencimiento.isoformat(), m.estado),  # Fechas en formato ISO
            )

    def actualizar(self, socio) -> None:  # Guarda los cambios de la membresía (ej: tras pagar)
        m = socio.membresia  # Obtiene la membresía actualizada
        with self.transaccion():  # Abre (o se une a) una transacción
            self.cursor.execute(  # Actualiza las fechas y el estado
                """UPDATE membresias SET fecha_inicio = ?, fecha_vencimiento = ?, estado = ?
                   WHERE socio_rut = ?""",  # Consulta parametrizada
                (m.fecha_inicio.isoformat(), m.fecha_vencimiento.isoformat(), m.estado, socio.rut),  # Nuevos valores
            )
