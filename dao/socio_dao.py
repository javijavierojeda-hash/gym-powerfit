from datetime import date  # Importa date para convertir el texto ISO en fecha
from dao.dao import Dao  # Importa la clase base Dao
from dao.membresia_dao import MembresiaDao  # Importa el DAO de la parte de la composición
from model.socio import Socio  # Importa la clase del modelo que este DAO construye
from model.validaciones import limpiar_rut  # Importa la normalización del RUT para las búsquedas


class SocioDao(Dao):  # Define la clase SocioDao que hereda de Dao
    """
    Data Access Object para la entidad Socio.
    Guarda y lee al socio JUNTO con su membresía (composición).
    """

    def crear_tabla(self):  # Define el método para crear la tabla de socios
        """
        Crea la tabla 'socios' si no existe:
        - rut: TEXT PRIMARY KEY (RUT normalizado 12345678-5)
        - nombre: TEXT NOT NULL
        """
        sql = """
        CREATE TABLE IF NOT EXISTS socios(
            rut TEXT PRIMARY KEY,
            nombre TEXT NOT NULL
        )
        """
        self.cursor.execute(sql)  # Ejecuta la consulta SQL para crear la tabla
        self.conexion.commit()  # Confirma los cambios en la base de datos

    def insertar(self, socio: Socio) -> None:  # Guarda un socio nuevo con su membresía
        """
        Inserta el socio y su membresía en UNA transacción: nunca queda un
        socio sin membresía ni una membresía sin socio.
        """
        with self.transaccion():  # Todo o nada
            self.cursor.execute(  # Inserta el socio
                "INSERT INTO socios(rut, nombre) VALUES (?, ?)",  # Consulta parametrizada
                (socio.rut, socio.nombre),  # RUT normalizado y nombre
            )
            MembresiaDao(self.conexion).insertar(socio)  # Inserta la membresía dentro de la MISMA transacción

    def existe(self, rut: str) -> bool:  # Indica si ya hay un socio con ese RUT
        fila = self.cursor.execute("SELECT 1 FROM socios WHERE rut = ?", (limpiar_rut(rut),)).fetchone()  # Busca el RUT
        return fila is not None  # True si encontró una fila

    def buscar_por_rut(self, rut: str) -> Socio | None:  # Busca un socio por su RUT
        sql = """
        SELECT s.rut, s.nombre, m.fecha_inicio, m.fecha_vencimiento
        FROM socios s
        JOIN membresias m ON m.socio_rut = s.rut
        WHERE s.rut = ?
        """  # Une el socio con su membresía
        fila = self.cursor.execute(sql, (limpiar_rut(rut),)).fetchone()  # Normaliza el RUT antes de buscar
        return self._construir(fila) if fila else None  # Convierte la fila en Socio o retorna None

    def listar(self, filtro: str = "") -> list[Socio]:  # Lista socios, opcionalmente filtrando por nombre o RUT
        sql = """
        SELECT s.rut, s.nombre, m.fecha_inicio, m.fecha_vencimiento
        FROM socios s
        JOIN membresias m ON m.socio_rut = s.rut
        WHERE s.nombre LIKE ? OR s.rut LIKE ?
        ORDER BY s.nombre
        """  # El filtro se aplica sobre nombre o RUT
        patron = f"%{filtro.strip().replace('.', '')}%"  # Arma el patrón LIKE (se quitan puntos para buscar RUT)
        return [self._construir(f) for f in self.cursor.execute(sql, (patron, patron)).fetchall()]  # Parámetros: nunca se concatena SQL

    def actualizar_nombre(self, socio: Socio) -> None:  # Guarda el cambio de nombre de un socio
        with self.transaccion():  # Abre una transacción
            self.cursor.execute("UPDATE socios SET nombre = ? WHERE rut = ?", (socio.nombre, socio.rut))  # Consulta parametrizada

    def _construir(self, fila) -> Socio:  # Convierte una fila en un objeto Socio con su membresía
        return Socio(  # Crea el socio con las fechas guardadas de su membresía
            fila["rut"],  # RUT
            fila["nombre"],  # Nombre
            date.fromisoformat(fila["fecha_inicio"]),  # Convierte el texto ISO a fecha
            date.fromisoformat(fila["fecha_vencimiento"]),  # Convierte el texto ISO a fecha
        )
