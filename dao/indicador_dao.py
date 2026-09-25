from datetime import datetime  # Importa datetime para guardar cuándo se obtuvo el valor
from dao.dao import Dao  # Importa la clase base Dao


class IndicadorDao(Dao):  # Define la clase IndicadorDao que hereda de Dao
    """
    Data Access Object para indicadores económicos (ej: el dólar del día).
    Guarda el último valor obtenido de la API para usarlo de respaldo
    si la API no responde.
    """

    def crear_tabla(self):  # Define el método para crear la tabla de indicadores
        """
        Crea la tabla 'indicadores' si no existe:
        - nombre: TEXT PRIMARY KEY (ej: 'dolar')
        - valor: REAL NOT NULL
        - fecha: TEXT NOT NULL (cuándo se obtuvo)
        """
        sql = """
        CREATE TABLE IF NOT EXISTS indicadores(
            nombre TEXT PRIMARY KEY,
            valor REAL NOT NULL,
            fecha TEXT NOT NULL
        )
        """
        self.cursor.execute(sql)  # Ejecuta la consulta SQL para crear la tabla
        self.conexion.commit()  # Confirma los cambios en la base de datos

    def guardar(self, nombre: str, valor: float) -> None:  # Guarda (o reemplaza) el valor de un indicador
        with self.transaccion():  # Abre una transacción
            self.cursor.execute(  # Inserta o reemplaza el valor
                """INSERT INTO indicadores(nombre, valor, fecha) VALUES (?, ?, ?)
                   ON CONFLICT(nombre) DO UPDATE SET valor = excluded.valor, fecha = excluded.fecha""",  # "upsert"
                (nombre, valor, datetime.now().isoformat(timespec="seconds")),  # Nombre, valor y fecha actual
            )

    def obtener(self, nombre: str):  # Obtiene el último valor guardado de un indicador
        fila = self.cursor.execute("SELECT valor, fecha FROM indicadores WHERE nombre = ?", (nombre,)).fetchone()  # Parametrizada
        return (fila["valor"], fila["fecha"]) if fila else None  # Retorna (valor, fecha) o None
