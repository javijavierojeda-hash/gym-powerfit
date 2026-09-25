from datetime import date, time  # Importa fecha y hora para convertir datos de la BD
from dao.dao import Dao  # Importa la clase base Dao
from model.clase import DIAS_SEMANA  # Importa el orden de los días para ordenar el horario
from model.yoga import Yoga  # Importa los tipos de clase para reconstruir objetos...
from model.spinning import Spinning  # ...del tipo correcto al leer desde la BD
from model.crossfit import Crossfit  # ...(Yoga, Spinning o Crossfit)


def mes_actual() -> str:  # Función auxiliar: mes de hoy en formato AAAA-MM
    return date.today().strftime("%Y-%m")  # Ej: "2026-10"


class ClaseDao(Dao):  # Define la clase ClaseDao que hereda de Dao
    """
    Data Access Object para la entidad Clase (padre en la herencia relacional).

    Crea la tabla 'clases'. Los hijos YogaDao, SpinningDao y CrossfitDao crean
    su tabla con id PK + FK hacia clases.id (tabla por tipo, como AutoDao).

    Los 'inscritos' NO se guardan como número fijo: se CUENTAN desde las
    reservas del mes. Así el cupo nunca queda desincronizado.

    Nota: las consultas de lectura usan las tablas hijas y la tabla de
    detalles, por lo que se debe crear el esquema completo (dao/esquema.py).
    """

    TABLA_HIJA: str | None = None  # El DAO padre no tiene tabla hija

    def crear_tabla(self):  # Método para crear la tabla base de clases
        """
        Crea la tabla 'clases' si no existe:
        - id: INTEGER PRIMARY KEY AUTOINCREMENT
        - dia: TEXT NOT NULL (lunes..domingo)
        - hora: TEXT NOT NULL (HH:MM)
        - duracion_min, cupo_maximo, precio_mensual: INTEGER NOT NULL (valores del tipo)
        - instructor_rut: TEXT (FK hacia instructores.rut) -> asociación "dicta" del UML
        """
        sql = """
        CREATE TABLE IF NOT EXISTS clases(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            dia TEXT NOT NULL,
            hora TEXT NOT NULL,
            duracion_min INTEGER NOT NULL,
            cupo_maximo INTEGER NOT NULL,
            precio_mensual INTEGER NOT NULL,
            instructor_rut TEXT,
            FOREIGN KEY (instructor_rut) REFERENCES instructores (rut) ON DELETE SET NULL
        )
        """
        self.cursor.execute(sql)  # Ejecuta la consulta SQL para crear la tabla
        self.conexion.commit()  # Confirma los cambios en la base de datos

    # ---------- Escritura ----------

    def insertar(self, clase) -> int:  # Guarda una clase nueva en 'clases' y en su tabla hija
        """
        Inserta la clase en la tabla padre y en la hija dentro de una
        transacción. Asigna el id generado al objeto y lo retorna.
        """
        if self.TABLA_HIJA is None:  # El DAO padre no sabe qué tipo de clase es
            raise NotImplementedError("Use YogaDao, SpinningDao o CrossfitDao")  # Obliga a usar el DAO concreto
        with self.transaccion():  # Todo o nada
            self.cursor.execute(  # Inserta los datos comunes
                """INSERT INTO clases(dia, hora, duracion_min, cupo_maximo, precio_mensual, instructor_rut)
                   VALUES (?, ?, ?, ?, ?, ?)""",  # Consulta parametrizada
                (clase.dia, f"{clase.hora:%H:%M}", clase.duracion_min,  # Día, hora como texto y duración
                 clase.cupo_maximo, clase.precio_mensual, clase.instructor_rut),  # Cupo, precio e instructor
            )
            clase.id = self.cursor.lastrowid  # Asigna al objeto el id que generó SQLite
            self._insertar_hija(clase)  # Inserta la fila de la tabla hija (cada DAO hijo sabe cómo)
        return clase.id  # Retorna el id nuevo

    def _insertar_hija(self, clase) -> None:  # Inserta la fila en la tabla hija (versión básica)
        self.cursor.execute(f"INSERT INTO {self.TABLA_HIJA}(id) VALUES (?)", (clase.id,))  # Solo el id (PK + FK)

    def actualizar_horario(self, clase_id: int, dia: str, hora: time) -> None:  # Cambia día y hora de una clase
        with self.transaccion():  # Abre una transacción
            self.cursor.execute(  # Actualiza el horario
                "UPDATE clases SET dia = ?, hora = ? WHERE id = ?",  # Consulta parametrizada
                (dia, f"{hora:%H:%M}", clase_id),  # Nuevo día, nueva hora e id de la clase
            )

    def eliminar(self, clase_id: int) -> None:  # Elimina una clase
        """
        Elimina la clase. Si tiene reservas, la FK de los detalles lo
        impide (sqlite3.IntegrityError): no se borra historia de cobros.
        """
        with self.transaccion():  # Abre una transacción
            self.cursor.execute("DELETE FROM clases WHERE id = ?", (clase_id,))  # Borra la fila (la hija se borra en cascada)

    # ---------- Lectura ----------

    _SELECT = """
        SELECT c.*, s.bicicletas_operativas,
               CASE WHEN y.id IS NOT NULL THEN 'yoga'
                    WHEN s.id IS NOT NULL THEN 'spinning'
                    WHEN x.id IS NOT NULL THEN 'crossfit' END AS tipo,
               (SELECT COUNT(*)
                  FROM detalles_clase_reservada d
                  JOIN inscripciones_mensuales i ON i.id = d.inscripcion_id
                 WHERE d.clase_id = c.id AND i.mes = ?) AS inscritos
          FROM clases c
          LEFT JOIN yoga y ON y.id = c.id
          LEFT JOIN spinning s ON s.id = c.id
          LEFT JOIN crossfit x ON x.id = c.id
    """  # Une la tabla padre con las tres hijas para saber el tipo, y cuenta los inscritos del mes

    def buscar_por_id(self, clase_id: int, mes: str | None = None):  # Busca una clase por su id
        """
        Retorna la clase (Yoga, Spinning o Crossfit) con los inscritos
        del mes indicado (por defecto, el mes actual), o None.
        """
        fila = self.cursor.execute(self._SELECT + " WHERE c.id = ?", (mes or mes_actual(), clase_id)).fetchone()  # Ejecuta la consulta
        return self._construir(fila) if fila else None  # Convierte la fila en objeto o retorna None

    def listar(self, mes: str | None = None, instructor_rut: str | None = None) -> list:  # Lista las clases
        """
        Lista todas las clases (o solo las de un instructor), ordenadas por
        día de la semana y hora, con los inscritos del mes.
        """
        sql = self._SELECT  # Parte de la consulta base
        parametros: list = [mes or mes_actual()]  # El primer parámetro es el mes para contar inscritos
        if instructor_rut:  # Si se pidió filtrar por instructor...
            sql += " WHERE c.instructor_rut = ?"  # ...agrega el filtro
            parametros.append(instructor_rut)  # ...y su valor
        clases = [self._construir(f) for f in self.cursor.execute(sql, parametros).fetchall()]  # Construye los objetos
        return sorted(clases, key=lambda c: (DIAS_SEMANA.index(c.dia), c.hora))  # Ordena lunes→domingo y por hora

    def _construir(self, fila):  # Convierte una fila en el objeto del tipo correcto
        hora = time.fromisoformat(fila["hora"])  # Convierte el texto "HH:MM" en objeto time
        datos = dict(dia=fila["dia"], hora=hora, instructor_rut=fila["instructor_rut"],  # Datos comunes a todas las clases
                     id=fila["id"], inscritos=fila["inscritos"])  # Id e inscritos contados del mes
        if fila["tipo"] == "yoga":  # Si la fila está en la tabla yoga...
            return Yoga(**datos)  # ...crea un objeto Yoga
        if fila["tipo"] == "spinning":  # Si está en la tabla spinning...
            return Spinning(**datos, bicicletas_operativas=fila["bicicletas_operativas"])  # ...crea Spinning con sus bicicletas
        if fila["tipo"] == "crossfit":  # Si está en la tabla crossfit...
            return Crossfit(**datos)  # ...crea un objeto Crossfit
        raise ValueError(f"La clase {fila['id']} no tiene tipo registrado")  # Dato inconsistente: se avisa
