from dao.dao import Dao  # Importa la clase base Dao


class DetalleClaseReservadaDao(Dao):  # Define la clase DetalleClaseReservadaDao que hereda de Dao
    """
    Data Access Object para la entidad DetalleClaseReservada.

    La composición InscripcionMensual ◆── DetalleClaseReservada se implementa
    con ON DELETE CASCADE: si se anula la inscripción, sus detalles se borran.
    La asociación con Clase NO es cascada: no se puede borrar una clase
    que tiene reservas (se protege la historia de cobros).
    """

    def crear_tabla(self):  # Define el método para crear la tabla de detalles
        """
        Crea la tabla 'detalles_clase_reservada' si no existe:
        - id: INTEGER PRIMARY KEY AUTOINCREMENT
        - inscripcion_id: INTEGER NOT NULL (FK a inscripciones_mensuales, CASCADE)
        - clase_id: INTEGER NOT NULL (FK a clases)
        - dia, hora: TEXT NOT NULL (copiados de la clase al reservar)
        - UNIQUE(inscripcion_id, clase_id): no se reserva dos veces la misma clase
        """
        sql = """
        CREATE TABLE IF NOT EXISTS detalles_clase_reservada(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            inscripcion_id INTEGER NOT NULL,
            clase_id INTEGER NOT NULL,
            dia TEXT NOT NULL,
            hora TEXT NOT NULL,
            UNIQUE (inscripcion_id, clase_id),
            FOREIGN KEY (inscripcion_id) REFERENCES inscripciones_mensuales (id) ON DELETE CASCADE,
            FOREIGN KEY (clase_id) REFERENCES clases (id)
        )
        """
        self.cursor.execute(sql)  # Ejecuta la consulta SQL para crear la tabla
        self.conexion.commit()  # Confirma los cambios en la base de datos

    def insertar(self, inscripcion_id: int, detalle) -> None:  # Guarda un detalle de una inscripción
        with self.transaccion():  # Abre (o se une a) una transacción
            self.cursor.execute(  # Inserta la fila del detalle
                """INSERT INTO detalles_clase_reservada(inscripcion_id, clase_id, dia, hora)
                   VALUES (?, ?, ?, ?)""",  # Consulta parametrizada
                (inscripcion_id, detalle.clase.id, detalle.dia, f"{detalle.hora:%H:%M}"),  # Valores del detalle
            )

    def listar_por_inscripcion(self, inscripcion_id: int) -> list:  # Obtiene las filas de detalle de una inscripción
        return self.cursor.execute(  # Ejecuta la consulta y retorna todas las filas
            "SELECT clase_id, dia, hora FROM detalles_clase_reservada WHERE inscripcion_id = ? ORDER BY id",  # Parametrizada
            (inscripcion_id,),  # Id de la inscripción
        ).fetchall()  # Lista de filas
