from dao.clase_dao import ClaseDao  # Importa ClaseDao para la herencia


class CrossfitDao(ClaseDao):  # CrossfitDao hereda de ClaseDao
    """
    Data Access Object para la entidad Crossfit.
    Hereda de ClaseDao (que a su vez hereda de Dao).
    """

    TABLA_HIJA = "crossfit"  # Tabla propia de este tipo de clase

    def crear_tabla(self):  # Sobrescribe crear_tabla para incluir la tabla hija
        """
        Crea la tabla padre 'clases' y luego la tabla 'crossfit':
        - id: INTEGER PRIMARY KEY, que a su vez es FOREIGN KEY de clases.id
        """
        super().crear_tabla()  # Primero asegura que exista la tabla padre 'clases'
        sql = """
        CREATE TABLE IF NOT EXISTS crossfit(
            id INTEGER PRIMARY KEY,
            FOREIGN KEY (id) REFERENCES clases (id) ON DELETE CASCADE
        )
        """
        self.cursor.execute(sql)  # Ejecuta la consulta de creación para la tabla hija
        self.conexion.commit()  # Confirma los cambios en la base de datos
