from dao.trabajador_dao import TrabajadorDao  # Importa TrabajadorDao para la herencia
from model.instructor import Instructor  # Importa la clase del modelo que este DAO construye


class InstructorDao(TrabajadorDao):  # InstructorDao hereda de TrabajadorDao (relación jerárquica)
    """
    Data Access Object para la entidad Instructor.
    Hereda de TrabajadorDao (que a su vez hereda de Dao), como AutoDao del profesor.
    """

    TABLA_HIJA = "instructores"  # Tabla propia de este tipo de trabajador
    CLASE_MODELO = Instructor  # Clase que se construye al leer desde la BD

    def crear_tabla(self):  # Sobrescribe crear_tabla para incluir la tabla hija
        """
        Invoca la creación de la tabla padre ('trabajadores') y luego crea
        la tabla 'instructores':
        - rut: TEXT PRIMARY KEY, que a su vez es FOREIGN KEY de trabajadores.rut
        """
        super().crear_tabla()  # Primero asegura que exista la tabla padre 'trabajadores'
        sql = """
        CREATE TABLE IF NOT EXISTS instructores(
            rut TEXT PRIMARY KEY,
            FOREIGN KEY (rut) REFERENCES trabajadores (rut) ON DELETE CASCADE
        )
        """
        self.cursor.execute(sql)  # Ejecuta la consulta de creación para la tabla hija
        self.conexion.commit()  # Confirma los cambios en la base de datos
