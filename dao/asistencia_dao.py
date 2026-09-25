import sqlite3  # Importa sqlite3 para reconocer el error de registro duplicado
from datetime import date  # Importa date para las fechas de asistencia
from dao.dao import Dao  # Importa la clase base Dao


class AsistenciaDao(Dao):  # Define la clase AsistenciaDao que hereda de Dao
    """
    Data Access Object para la asistencia a clases.

    No aparece como clase en el UML original, pero el método
    Instructor.marcar_asistencia() necesita un lugar donde guardar el registro.
    """

    def crear_tabla(self):  # Define el método para crear la tabla de asistencias
        """
        Crea la tabla 'asistencias' si no existe:
        - id: INTEGER PRIMARY KEY AUTOINCREMENT
        - clase_id: INTEGER NOT NULL (FK a clases)
        - socio_rut: TEXT NOT NULL (FK a socios)
        - fecha: TEXT NOT NULL (AAAA-MM-DD)
        - instructor_rut: TEXT (FK a instructores): quién la marcó
        - UNIQUE(clase_id, socio_rut, fecha): una asistencia por socio, clase y día
        """
        sql = """
        CREATE TABLE IF NOT EXISTS asistencias(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            clase_id INTEGER NOT NULL,
            socio_rut TEXT NOT NULL,
            fecha TEXT NOT NULL,
            instructor_rut TEXT,
            UNIQUE (clase_id, socio_rut, fecha),
            FOREIGN KEY (clase_id) REFERENCES clases (id) ON DELETE CASCADE,
            FOREIGN KEY (socio_rut) REFERENCES socios (rut) ON DELETE CASCADE,
            FOREIGN KEY (instructor_rut) REFERENCES instructores (rut) ON DELETE SET NULL
        )
        """
        self.cursor.execute(sql)  # Ejecuta la consulta SQL para crear la tabla
        self.conexion.commit()  # Confirma los cambios en la base de datos

    def registrar(self, clase_id: int, socio_rut: str, instructor_rut: str, fecha: date | None = None) -> None:  # Marca asistencia
        try:  # Intenta insertar el registro
            with self.transaccion():  # Abre una transacción
                self.cursor.execute(  # Inserta la asistencia
                    "INSERT INTO asistencias(clase_id, socio_rut, fecha, instructor_rut) VALUES (?, ?, ?, ?)",  # Parametrizada
                    (clase_id, socio_rut, (fecha or date.today()).isoformat(), instructor_rut),  # Valores del registro
                )
        except sqlite3.IntegrityError:  # Si la restricción UNIQUE detecta un duplicado...
            raise ValueError("La asistencia ya estaba registrada")  # ...se informa con un mensaje claro

    def eliminar(self, clase_id: int, socio_rut: str, fecha: date | None = None) -> None:  # Desmarca una asistencia
        with self.transaccion():  # Abre una transacción
            self.cursor.execute(  # Borra el registro
                "DELETE FROM asistencias WHERE clase_id = ? AND socio_rut = ? AND fecha = ?",  # Parametrizada
                (clase_id, socio_rut, (fecha or date.today()).isoformat()),  # Clase, socio y fecha
            )

    def ruts_presentes(self, clase_id: int, fecha: date | None = None) -> set[str]:  # RUT de los socios presentes
        filas = self.cursor.execute(  # Consulta las asistencias de la clase en la fecha
            "SELECT socio_rut FROM asistencias WHERE clase_id = ? AND fecha = ?",  # Parametrizada
            (clase_id, (fecha or date.today()).isoformat()),  # Clase y fecha
        ).fetchall()  # Lista de filas
        return {f["socio_rut"] for f in filas}  # Retorna un conjunto (búsqueda rápida con "in")
