from contextlib import contextmanager  # Importa el decorador para crear bloques "with" propios


class Dao:  # Define la clase base Dao (Data Access Object)
    """
    Clase base Data Access Object (DAO).
    Se encarga de mantener la conexión a la base de datos y su cursor
    (igual que en el repo del profesor) y agrega un manejador de
    transacciones para que las operaciones de varios pasos sean atómicas:
    o se guardan TODAS, o no se guarda NINGUNA.
    """

    def __init__(self, conexion):  # Define el constructor de la clase, recibe la conexión
        """
        Constructor que recibe un objeto de conexión y establece el cursor.

        Args:
            conexion: El objeto de conexión a la base de datos.
        """
        self.conexion = conexion  # Almacena el objeto de conexión como un atributo de la instancia
        self.cursor = self.conexion.cursor()  # Crea y almacena un cursor para ejecutar consultas SQL

    @contextmanager
    def transaccion(self):  # Define un bloque "with self.transaccion():" para agrupar operaciones
        """
        Abre una transacción, ejecuta el bloque y confirma (commit).
        Si ocurre cualquier error, deshace todo (rollback) y relanza el error.

        Si ya existe una transacción abierta (por ejemplo, un DAO que llama
        a otro DAO), se une a ella en vez de abrir una nueva: así el commit
        o rollback lo decide la operación "de afuera".
        """
        if self.conexion.in_transaction:  # Si ya hay una transacción en curso...
            yield self.cursor  # ...solo ejecuta el bloque dentro de ella
            return  # ...y no hace commit: lo hará quien la abrió
        self.conexion.execute("BEGIN IMMEDIATE")  # Abre la transacción y reserva la escritura (evita que dos reservas choquen)
        try:  # Intenta ejecutar el bloque
            yield self.cursor  # Entrega el cursor al código dentro del "with"
            self.conexion.commit()  # Si todo salió bien, confirma los cambios en la base de datos
        except Exception:  # Si ocurrió cualquier error...
            self.conexion.rollback()  # ...deshace TODOS los cambios de la transacción
            raise  # ...y relanza el error para que quien llamó sepa qué pasó
