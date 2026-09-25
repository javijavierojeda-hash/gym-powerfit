"""
Configuración compartida de las pruebas (pytest carga este archivo solo).

Las "fixtures" son piezas reutilizables que pytest entrega a cada prueba
que las pide por nombre en sus parámetros.
"""

import re  # Para extraer el token CSRF del HTML
import pytest  # Framework de pruebas
import conectar  # Conexión a la BD
from dao.esquema import crear_esquema  # Crea las tablas
from services.dolar_service import DolarService  # Servicio del dólar (se aísla de internet)
from web import seguridad  # Para reiniciar el contador de intentos de login


@pytest.fixture(autouse=True)  # autouse: se aplica a TODAS las pruebas automáticamente
def sin_internet(monkeypatch):  # Evita que las pruebas dependan de la API real del dólar
    def api_caida(self):  # Función falsa que simula que la API no responde
        raise OSError("sin conexion en pruebas")  # Lanza un error de red
    monkeypatch.setattr(DolarService, "_obtener_json_desde_api", api_caida)  # Reemplaza la llamada real
    DolarService.limpiar_cache()  # Parte cada prueba sin caché
    seguridad._intentos.clear()  # Parte cada prueba sin intentos fallidos acumulados
    yield  # Ejecuta la prueba
    DolarService.limpiar_cache()  # Limpia al terminar


@pytest.fixture
def conexion():  # Base de datos vacía en memoria (se destruye al terminar)
    conn = conectar.crear_conexion(":memory:")  # BD temporal en RAM: nunca toca powerfit.db
    crear_esquema(conn)  # Crea todas las tablas
    yield conn  # Entrega la conexión a la prueba
    conn.close()  # La cierra al terminar


@pytest.fixture
def app(tmp_path):  # Aplicación web con una BD temporal y datos de ejemplo
    from web import create_app  # Importa la fábrica de la app
    return create_app({  # Crea una app aislada para las pruebas
        "TESTING": True,  # Modo prueba de Flask
        "DATABASE": str(tmp_path / "prueba.db"),  # BD en una carpeta temporal
        "CARGAR_DEMO": True,  # Carga los datos de ejemplo de seed.py
        "SECRET_KEY": "clave-de-prueba",  # Clave fija para las pruebas
    })


@pytest.fixture
def cliente(app):  # Navegador simulado para hacer peticiones a la app
    return app.test_client()  # Cliente de pruebas de Flask


def token(html: str) -> str:  # Extrae el token CSRF de una página
    return re.search(r'name="csrf_token" value="([^"]+)"', html).group(1)  # Busca el campo oculto


def iniciar_sesion(cliente, rut: str, password: str):  # Inicia sesión en el cliente simulado
    t = token(cliente.get("/login").text)  # Obtiene el token del formulario de login
    return cliente.post("/login", data={"rut": rut, "password": password, "csrf_token": t})  # Envía el formulario


@pytest.fixture
def recepcion(cliente):  # Cliente con sesión de recepcionista
    iniciar_sesion(cliente, "22.222.222-2", "Recepcion123!")  # Login de la recepcionista de ejemplo
    return cliente  # Retorna el cliente logueado


@pytest.fixture
def instructor(cliente):  # Cliente con sesión de instructor
    iniciar_sesion(cliente, "11.111.111-1", "Instructor123!")  # Login de la instructora de ejemplo
    return cliente  # Retorna el cliente logueado
