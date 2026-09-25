from dao.clase_dao import ClaseDao  # Importa ClaseDao para la herencia


class SpinningDao(ClaseDao):  # SpinningDao hereda de ClaseDao
    """
    Data Access Object para la entidad Spinning.
    Su tabla hija guarda un dato propio: las bicicletas operativas
    (igual que un Camion guardaría su capacidad de carga).
    """

    TABLA_HIJA = "spinning"  # Tabla propia de este tipo de clase

    def crear_tabla(self):  # Sobrescribe crear_tabla para incluir la tabla hija
        """
        Crea la tabla padre 'clases' y luego la tabla 'spinning':
        - id: INTEGER PRIMARY KEY + FOREIGN KEY de clases.id
        - bicicletas_operativas: INTEGER NOT NULL entre 0 y 15 (CHECK)
        """
        super().crear_tabla()  # Primero asegura que exista la tabla padre 'clases'
        sql = """
        CREATE TABLE IF NOT EXISTS spinning(
            id INTEGER PRIMARY KEY,
            bicicletas_operativas INTEGER NOT NULL CHECK (bicicletas_operativas BETWEEN 0 AND 15),
            FOREIGN KEY (id) REFERENCES clases (id) ON DELETE CASCADE
        )
        """
        self.cursor.execute(sql)  # Ejecuta la consulta de creación para la tabla hija
        self.conexion.commit()  # Confirma los cambios en la base de datos

    def _insertar_hija(self, clase) -> None:  # Sobrescribe la inserción de la fila hija
        self.cursor.execute(  # Inserta el id y las bicicletas operativas
            "INSERT INTO spinning(id, bicicletas_operativas) VALUES (?, ?)",  # Consulta parametrizada
            (clase.id, clase.bicicletas_operativas),  # Valores de la clase Spinning
        )

    def actualizar_bicicletas(self, clase_id: int, cantidad: int) -> None:  # Registra bicicletas en mantención
        with self.transaccion():  # Abre una transacción
            self.cursor.execute(  # Actualiza la cantidad de bicicletas que funcionan
                "UPDATE spinning SET bicicletas_operativas = ? WHERE id = ?",  # Consulta parametrizada
                (cantidad, clase_id),  # Nueva cantidad e id de la clase
            )
