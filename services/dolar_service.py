"""
Servicio que obtiene el valor del dólar del día (requerimiento 6).

Fuente: API pública chilena mindicador.cl (datos del Banco Central).
Diseño seguro y tolerante a fallos:
- Timeout corto: si la API no responde, la página no se queda "colgada".
- Validación: solo se acepta un número positivo y en un rango razonable.
- Caché de 1 hora en memoria: no se consulta la API en cada venta.
- Respaldo: si la API falla, se usa el último valor guardado en la BD
  (tabla 'indicadores') y, si no hay ninguno, un valor por defecto.
"""

import json  # Librería estándar para interpretar la respuesta JSON de la API
import time  # Librería estándar para medir cuánto dura la caché
import urllib.request  # Librería estándar para hacer peticiones HTTP (sin instalar nada extra)
from dataclasses import dataclass  # Permite crear clases de datos simples
from dao.indicador_dao import IndicadorDao  # DAO para guardar/leer el último valor conocido

URL_API = "https://mindicador.cl/api/dolar"  # Dirección de la API del dólar
VALOR_POR_DEFECTO = 950.0  # Valor de emergencia si nunca se pudo obtener uno real
RANGO_VALIDO = (100.0, 5000.0)  # Rango de sanidad: un dólar fuera de esto es un dato erróneo
DURACION_CACHE_SEG = 3600  # La cotización obtenida se reutiliza por 1 hora
DURACION_CACHE_FALLO_SEG = 600  # Si la API falló, no se reintenta hasta 10 minutos después


@dataclass(frozen=True)  # frozen=True: el objeto no se puede modificar después de crearlo
class Cotizacion:  # Resultado de consultar el dólar
    valor: float  # Valor del dólar en pesos chilenos
    fuente: str  # De dónde salió: "api", "respaldo" o "por defecto"
    fecha: str  # Fecha del dato


class DolarService:  # Define el servicio del dólar
    """
    Entrega la cotización del dólar del día con caché y respaldo.
    """

    _cache: dict = {"cotizacion": None, "expira": 0.0}  # Caché compartida por todas las instancias (vive en memoria)

    def __init__(self, conexion=None, obtener_json=None, timeout: float = 5.0) -> None:  # Constructor
        """
        Args:
            conexion: conexión a la BD para guardar/leer el valor de respaldo.
            obtener_json: función alternativa para obtener el JSON (se usa en
                          las pruebas para no depender de internet).
            timeout: segundos máximos de espera a la API.
        """
        self.__conexion = conexion  # Guarda la conexión (puede ser None)
        self.__obtener_json = obtener_json or self._obtener_json_desde_api  # Usa la función de prueba o la real
        self.__timeout = timeout  # Guarda el tiempo máximo de espera

    @classmethod
    def limpiar_cache(cls) -> None:  # Borra la caché (útil en pruebas o para forzar una actualización)
        cls._cache = {"cotizacion": None, "expira": 0.0}  # Reinicia la caché

    def obtener_cotizacion(self) -> Cotizacion:  # Método principal: retorna el dólar del día
        cache = DolarService._cache  # Obtiene la caché compartida
        if cache["cotizacion"] and time.monotonic() < cache["expira"]:  # Si hay un valor y no ha expirado...
            return cache["cotizacion"]  # ...lo reutiliza sin llamar a la API
        try:  # Intenta obtener el valor real desde la API
            datos = self.__obtener_json()  # Descarga y decodifica el JSON
            cotizacion = self._interpretar(datos)  # Extrae y valida el valor
            self._guardar_respaldo(cotizacion.valor)  # Guarda el valor en la BD para usarlo si la API falla después
            duracion = DURACION_CACHE_SEG  # Un valor real se guarda en caché por 1 hora
        except Exception:  # Si falla la red, el JSON o la validación...
            cotizacion = self._respaldo()  # ...usa el último valor conocido o el valor por defecto
            duracion = DURACION_CACHE_FALLO_SEG  # ...y reintenta en 10 minutos
        DolarService._cache = {"cotizacion": cotizacion, "expira": time.monotonic() + duracion}  # Actualiza la caché
        return cotizacion  # Retorna la cotización obtenida

    def obtener_valor(self) -> float:  # Atajo: solo el número del dólar
        return self.obtener_cotizacion().valor  # Retorna el valor

    # ---------- Métodos internos ----------

    def _obtener_json_desde_api(self) -> dict:  # Hace la petición HTTP real a la API
        peticion = urllib.request.Request(URL_API, headers={"User-Agent": "PowerFit/1.0"})  # Arma la petición con un identificador
        with urllib.request.urlopen(peticion, timeout=self.__timeout) as respuesta:  # Abre la conexión con timeout
            return json.loads(respuesta.read().decode("utf-8"))  # Lee, decodifica y convierte el JSON a diccionario

    @staticmethod
    def _interpretar(datos: dict) -> Cotizacion:  # Extrae y VALIDA el valor desde el JSON
        """
        La API responde {"serie": [{"fecha": "...", "valor": 950.12}, ...]}.
        Se valida que el valor sea numérico y esté en un rango razonable
        antes de usarlo (nunca se confía ciegamente en datos externos).
        """
        primero = datos["serie"][0]  # Toma el dato más reciente de la serie
        valor = primero["valor"]  # Obtiene el valor del dólar
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):  # Debe ser un número (bool se excluye explícitamente)
            raise ValueError("La API entrego un valor no numerico")  # Rechaza datos extraños
        if not RANGO_VALIDO[0] <= valor <= RANGO_VALIDO[1]:  # Revisa el rango de sanidad
            raise ValueError("La API entrego un valor fuera de rango")  # Rechaza valores absurdos
        return Cotizacion(float(valor), "api", str(primero.get("fecha", ""))[:10])  # Retorna la cotización validada

    def _guardar_respaldo(self, valor: float) -> None:  # Guarda el último valor real en la BD
        if self.__conexion is not None:  # Solo si hay una conexión disponible
            IndicadorDao(self.__conexion).guardar("dolar", valor)  # Guarda o reemplaza el valor 'dolar'

    def _respaldo(self) -> Cotizacion:  # Obtiene un valor cuando la API no está disponible
        if self.__conexion is not None:  # Si hay BD...
            guardado = IndicadorDao(self.__conexion).obtener("dolar")  # ...busca el último valor guardado
            if guardado:  # Si existe...
                return Cotizacion(guardado[0], "respaldo", guardado[1][:10])  # ...lo usa como respaldo
        return Cotizacion(VALOR_POR_DEFECTO, "por defecto", "")  # Último recurso: el valor por defecto
