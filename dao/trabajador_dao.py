from dao.dao import Dao  # Importa la clase base Dao


class TrabajadorDao(Dao):  # Define la clase TrabajadorDao que hereda de Dao
    """
    Data Access Object para la entidad Trabajador (padre en la herencia relacional).

    Igual que VehiculoDao del profesor: crea la tabla padre 'trabajadores'.
    Los DAOs hijos (InstructorDao y RecepcionistaDao) crean su propia tabla
    cuya llave primaria es también llave foránea hacia 'trabajadores'
    (estrategia "tabla por tipo" / table-per-type).

    Los hijos definen:
      - TABLA_HIJA:  nombre de su tabla ('instructores' o 'recepcionistas').
      - CLASE_MODELO: la clase Python que construyen (Instructor o Recepcionista).
    """

    TABLA_HIJA: str | None = None  # El DAO padre no tiene tabla hija
    CLASE_MODELO = None  # El DAO padre no construye objetos (Trabajador es abstracta)

    def crear_tabla(self):  # Método para crear la tabla base de trabajadores
        """
        Crea la tabla 'trabajadores' si no existe:
        - rut: TEXT PRIMARY KEY (RUT normalizado 12345678-5)
        - nombre: TEXT NOT NULL
        - password_hash: TEXT NOT NULL (hash PBKDF2, nunca la contraseña)
        """
        sql = """
        CREATE TABLE IF NOT EXISTS trabajadores(
            rut TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            password_hash TEXT NOT NULL
        )
        """
        self.cursor.execute(sql)  # Ejecuta la instrucción de creación de tabla
        self.conexion.commit()  # Confirma los cambios realizados

    def insertar(self, trabajador):  # Guarda un trabajador en la tabla padre y en su tabla hija
        """
        Inserta el trabajador en 'trabajadores' y en la tabla del hijo,
        dentro de una sola transacción (se guardan las dos filas o ninguna).
        """
        if self.TABLA_HIJA is None:  # El DAO padre no sabe en qué tabla hija guardar
            raise NotImplementedError("Use InstructorDao o RecepcionistaDao")  # Obliga a usar el DAO concreto
        with self.transaccion():  # Abre una transacción: todo o nada
            self.cursor.execute(  # Inserta la fila en la tabla padre
                "INSERT INTO trabajadores(rut, nombre, password_hash) VALUES (?, ?, ?)",  # Consulta PARAMETRIZADA (evita inyección SQL)
                (trabajador.rut, trabajador.nombre, trabajador.exportar_hash()),  # Valores que reemplazan a los "?"
            )
            self.cursor.execute(  # Inserta la fila en la tabla hija
                f"INSERT INTO {self.TABLA_HIJA}(rut) VALUES (?)",  # El nombre de tabla es una constante interna, no viene del usuario
                (trabajador.rut,),  # El RUT es PK y FK al mismo tiempo
            )

    def buscar_por_rut(self, rut: str):  # Busca un trabajador del tipo de este DAO
        """
        Retorna el objeto (Instructor o Recepcionista) con ese RUT, o None.
        """
        sql = f"""
        SELECT t.rut, t.nombre, t.password_hash
        FROM trabajadores t
        JOIN {self.TABLA_HIJA} h ON h.rut = t.rut
        WHERE t.rut = ?
        """  # El JOIN asegura que el RUT pertenezca a este tipo de trabajador
        fila = self.cursor.execute(sql, (rut,)).fetchone()  # Ejecuta la consulta y toma la primera fila
        return self._construir(fila) if fila else None  # Convierte la fila en objeto, o retorna None

    def listar(self) -> list:  # Lista todos los trabajadores de este tipo
        sql = f"""
        SELECT t.rut, t.nombre, t.password_hash
        FROM trabajadores t
        JOIN {self.TABLA_HIJA} h ON h.rut = t.rut
        ORDER BY t.nombre
        """  # Ordena alfabéticamente por nombre
        return [self._construir(fila) for fila in self.cursor.execute(sql).fetchall()]  # Convierte cada fila en objeto

    def actualizar_password(self, trabajador) -> None:  # Guarda el nuevo hash de contraseña
        with self.transaccion():  # Abre una transacción
            self.cursor.execute(  # Actualiza solo el hash
                "UPDATE trabajadores SET password_hash = ? WHERE rut = ?",  # Consulta parametrizada
                (trabajador.exportar_hash(), trabajador.rut),  # Nuevo hash y RUT del trabajador
            )

    def _construir(self, fila):  # Convierte una fila de la BD en un objeto del modelo
        return self.CLASE_MODELO(fila["rut"], fila["nombre"], fila["password_hash"])  # Crea Instructor o Recepcionista
