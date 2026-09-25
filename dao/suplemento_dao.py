from datetime import datetime  # Importa datetime para registrar la fecha y hora de cada venta
from dao.dao import Dao  # Importa la clase base Dao
from model.suplemento import Suplemento  # Importa la clase del modelo que este DAO construye


class SuplementoDao(Dao):  # Define la clase SuplementoDao que hereda de Dao
    """
    Data Access Object para la entidad Suplemento y el registro de sus ventas.
    """

    def crear_tabla(self):  # Define el método para crear las tablas de suplementos y ventas
        """
        Crea la tabla 'suplementos':
        - codigo: TEXT PRIMARY KEY
        - nombre: TEXT NOT NULL
        - stock: INTEGER NOT NULL, CHECK >= 0 (la BD nunca acepta stock negativo)
        - precio_usd: REAL NOT NULL, CHECK > 0
        - precio_clp: INTEGER NOT NULL (último precio calculado con el dólar)
        y la tabla 'ventas_suplemento' con el historial de ventas
        (asociación "vende" entre Recepcionista y Suplemento).
        """
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS suplementos(
            codigo TEXT PRIMARY KEY,
            nombre TEXT NOT NULL,
            stock INTEGER NOT NULL CHECK (stock >= 0),
            precio_usd REAL NOT NULL CHECK (precio_usd > 0),
            precio_clp INTEGER NOT NULL DEFAULT 0
        )
        """)  # Ejecuta la creación de la tabla de productos
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS ventas_suplemento(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            codigo TEXT NOT NULL,
            cantidad INTEGER NOT NULL CHECK (cantidad > 0),
            valor_dolar REAL NOT NULL,
            total_clp INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            recepcionista_rut TEXT,
            FOREIGN KEY (codigo) REFERENCES suplementos (codigo),
            FOREIGN KEY (recepcionista_rut) REFERENCES recepcionistas (rut) ON DELETE SET NULL
        )
        """)  # Ejecuta la creación de la tabla de ventas
        self.conexion.commit()  # Confirma los cambios en la base de datos

    def insertar(self, s: Suplemento) -> None:  # Guarda un suplemento nuevo
        with self.transaccion():  # Abre una transacción
            self.cursor.execute(  # Inserta el producto
                "INSERT INTO suplementos(codigo, nombre, stock, precio_usd, precio_clp) VALUES (?, ?, ?, ?, ?)",  # Parametrizada
                (s.codigo, s.nombre, s.stock, s.precio_usd, s.precio_clp),  # Valores del suplemento
            )

    def buscar(self, codigo: str) -> Suplemento | None:  # Busca un suplemento por código
        fila = self.cursor.execute("SELECT * FROM suplementos WHERE codigo = ?", (codigo.strip().upper(),)).fetchone()  # Parametrizada
        return self._construir(fila) if fila else None  # Convierte la fila o retorna None

    def listar(self) -> list[Suplemento]:  # Lista todos los suplementos
        return [self._construir(f) for f in self.cursor.execute("SELECT * FROM suplementos ORDER BY nombre").fetchall()]  # Ordenados por nombre

    def actualizar_precios(self, suplementos: list[Suplemento]) -> None:  # Guarda los precios en CLP recalculados
        with self.transaccion():  # Una sola transacción para todos los productos
            self.cursor.executemany(  # Ejecuta la misma consulta para cada suplemento
                "UPDATE suplementos SET precio_clp = ? WHERE codigo = ?",  # Parametrizada
                [(s.precio_clp, s.codigo) for s in suplementos],  # Lista de pares (precio, código)
            )

    def registrar_venta(self, s: Suplemento, cantidad: int, total_clp: int, valor_dolar: float,  # Guarda una venta
                        recepcionista_rut: str | None = None) -> None:
        """
        Descuenta el stock y registra la venta en UNA transacción.
        El UPDATE solo funciona si hay stock suficiente ("stock >= ?"),
        así dos ventas simultáneas nunca dejan el stock negativo.
        """
        with self.transaccion():  # Todo o nada
            self.cursor.execute(  # Descuenta stock solo si alcanza
                "UPDATE suplementos SET stock = stock - ? WHERE codigo = ? AND stock >= ?",  # Condición de stock en la misma consulta
                (cantidad, s.codigo, cantidad),  # Cantidad, código y cantidad mínima requerida
            )
            if self.cursor.rowcount != 1:  # Si no se actualizó la fila...
                raise ValueError("Stock insuficiente para realizar la venta")  # ...se cancela la venta completa
            self.cursor.execute(  # Registra la venta en el historial
                """INSERT INTO ventas_suplemento(codigo, cantidad, valor_dolar, total_clp, fecha, recepcionista_rut)
                   VALUES (?, ?, ?, ?, ?, ?)""",  # Parametrizada
                (s.codigo, cantidad, valor_dolar, total_clp, datetime.now().isoformat(timespec="seconds"), recepcionista_rut),  # Datos de la venta
            )

    def listar_ventas(self, limite: int = 10) -> list:  # Últimas ventas realizadas
        return self.cursor.execute(  # Une ventas con el nombre del producto
            """SELECT v.*, s.nombre FROM ventas_suplemento v
               JOIN suplementos s ON s.codigo = v.codigo
               ORDER BY v.id DESC LIMIT ?""",  # Más recientes primero
            (limite,),  # Cantidad máxima de filas
        ).fetchall()  # Lista de filas

    def _construir(self, fila) -> Suplemento:  # Convierte una fila en un objeto Suplemento
        return Suplemento(fila["codigo"], fila["nombre"], fila["stock"], fila["precio_usd"], fila["precio_clp"])  # Crea el objeto
