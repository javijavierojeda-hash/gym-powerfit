"""
Clase abstracta Trabajador: lo común a instructores y recepcionistas.

Es abstracta porque el gimnasio siempre contrata un instructor o una
recepcionista, nunca un "trabajador genérico".

SEGURIDAD: la contraseña NUNCA se guarda en texto plano. Se guarda un hash
PBKDF2-SHA256 con "salt" aleatorio, y la comparación se hace en tiempo
constante para evitar ataques por tiempo de respuesta (timing attacks).
"""

import hashlib  # Librería estándar con funciones de hash (PBKDF2)
import hmac  # Librería estándar con compare_digest (comparación en tiempo constante)
import secrets  # Librería estándar para generar valores aleatorios seguros
from abc import ABC, abstractmethod  # Herramientas para crear clases abstractas
from model.validaciones import es_rut_valido, limpiar_rut, formatear_rut  # Utilidades de RUT

_ALGORITMO = "pbkdf2_sha256"  # Nombre del algoritmo que se guarda junto al hash
_ITERACIONES = 260_000  # Cantidad de vueltas del hash: más vueltas = más difícil adivinar por fuerza bruta
_LARGO_MINIMO = 8  # Largo mínimo exigido para una contraseña


class Trabajador(ABC):  # Hereda de ABC: no se puede instanciar directamente
    """
    Base de Instructor y Recepcionista: RUT, nombre y contraseña cifrada.
    """

    def __init__(self, rut: str, nombre: str, password_hash: str) -> None:  # Constructor común
        if not es_rut_valido(rut):  # El RUT del trabajador también se valida
            raise ValueError(f"RUT invalido: {rut}")  # Rechaza RUT mal formados
        if not nombre or not nombre.strip():  # El nombre es obligatorio
            raise ValueError("El nombre del trabajador es obligatorio")  # Rechaza nombres vacíos
        if not isinstance(password_hash, str) or not password_hash.startswith(_ALGORITMO + "$"):  # Exige un hash real
            raise ValueError("password_hash invalido: use Trabajador.generar_hash()")  # Impide guardar contraseñas en texto plano
        self.__rut: str = limpiar_rut(rut)  # Atributo privado: RUT normalizado
        self.__nombre: str = nombre.strip()  # Atributo privado: nombre
        self.__password_hash: str = password_hash  # Atributo privado: hash (sin getter público, nunca se expone)

    # ---------- Propiedades ----------

    @property
    def rut(self) -> str:  # Getter del RUT
        return self.__rut  # Retorna el RUT normalizado

    @property
    def rut_formateado(self) -> str:  # RUT con puntos para mostrar
        return formatear_rut(self.__rut)  # Ej: 11.111.111-1

    @property
    def nombre(self) -> str:  # Getter del nombre
        return self.__nombre  # Retorna el nombre

    @property
    @abstractmethod
    def rol(self) -> str:  # Propiedad ABSTRACTA: cada subclase dice cuál es su rol
        """Nombre del rol ('instructor' o 'recepcionista'), usado para los permisos."""

    # ---------- Seguridad de la contraseña ----------

    @staticmethod
    def generar_hash(password: str) -> str:  # Crea el hash seguro de una contraseña
        """
        Genera 'pbkdf2_sha256$iteraciones$salt$hash' a partir de la contraseña.
        Cada llamada usa un salt distinto, así dos contraseñas iguales
        producen hashes diferentes.
        """
        if not isinstance(password, str) or len(password) < _LARGO_MINIMO:  # Exige un largo mínimo
            raise ValueError(f"La contrasena debe tener al menos {_LARGO_MINIMO} caracteres")  # Rechaza claves débiles
        salt = secrets.token_hex(16)  # Genera 16 bytes aleatorios seguros (32 caracteres hex)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), _ITERACIONES)  # Calcula el hash PBKDF2
        return f"{_ALGORITMO}${_ITERACIONES}${salt}${digest.hex()}"  # Guarda todo lo necesario para verificar después

    def login(self, password: str) -> bool:  # Método del UML: verifica la contraseña
        """
        Retorna True si la contraseña coincide con el hash guardado.
        """
        try:  # Protege contra hashes mal formados
            algoritmo, iteraciones, salt, hash_guardado = self.__password_hash.split("$")  # Separa las partes del hash
        except ValueError:  # Si el hash no tiene 4 partes...
            return False  # ...el login falla de forma segura
        if algoritmo != _ALGORITMO or not isinstance(password, str):  # Revisa algoritmo y tipo de dato
            return False  # Falla de forma segura
        calculado = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), int(iteraciones))  # Recalcula el hash con el mismo salt
        return hmac.compare_digest(calculado.hex(), hash_guardado)  # Compara en tiempo constante (evita timing attacks)

    def cambiar_password(self, actual: str, nueva: str) -> None:  # Permite cambiar la contraseña de forma segura
        if not self.login(actual):  # Exige conocer la contraseña actual
            raise PermissionError("La contrasena actual no es correcta")  # Bloquea el cambio
        self.__password_hash = Trabajador.generar_hash(nueva)  # Guarda el hash de la nueva contraseña

    def exportar_hash(self) -> str:  # Uso exclusivo del DAO para guardar en la base de datos
        return self.__password_hash  # Retorna el hash (nunca la contraseña)

    def __str__(self) -> str:  # Representación en texto
        return f"{self.__nombre} ({self.rol})"  # Ej: "Camila Rojas (instructor)"
