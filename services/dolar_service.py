"""
Servicio que obtiene el valor del dólar del día (requerimiento 6).

Fuente: API pública chilena mindicador.cl (datos del Banco Central).
La consulta usa la librería requests y queda TODA en esta clase (no
repartida por el código). Diseño seguro y tolerante a fallos:
- Timeout corto: si la API no responde, el programa no se queda "colgado".
- Cada falla se informa con su causa: sin conexión, demora o respuesta
  inesperada (no se esconde con un except genérico).
- Validación: solo se acepta un número positivo y en un rango razonable.
- Caché de 1 hora en memoria: no se consulta la API en cada venta.
- Respaldo: si la API falla, se usa el último valor guardado en la BD
  (tabla 'indicadores') y, si no hay ninguno, un valor por defecto.
"""

from __future__ import annotations  # Permite usar anotaciones modernas (str | None) también en Python 3.7 a 3.9

import time  # Librería estándar para medir cuánto dura la caché
from dataclasses import dataclass  # Permite crear clases de datos simples
import requests  # Librería para consumir APIs por HTTP (pip install requests)
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
    aviso: str = ""  # Si no se pudo usar la API: el motivo, para informarlo al usuario


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
        except requests.exceptions.Timeout:  # La API tardó más que el tiempo máximo de espera
            cotizacion = self._respaldo(f"la API del dolar no respondio en {self.__timeout:.0f} segundos")  # Informa la demora
            duracion = DURACION_CACHE_FALLO_SEG  # Reintenta en 10 minutos
        except requests.exceptions.ConnectionError:  # No hay internet o no se encontró el servidor
            cotizacion = self._respaldo("no hay conexion con la API del dolar (revise internet)")  # Informa la falta de conexión
            duracion = DURACION_CACHE_FALLO_SEG  # Reintenta en 10 minutos
        except requests.exceptions.HTTPError as error:  # La API respondió con un error (404, 500, ...)
            cotizacion = self._respaldo(f"la API del dolar respondio con error HTTP {error.response.status_code if error.response is not None else ''}".strip())  # Informa el código
            duracion = DURACION_CACHE_FALLO_SEG  # Reintenta en 10 minutos
        except (ValueError, KeyError, IndexError, TypeError):  # JSON inválido, sin "serie", vacío o con un valor que no es número
            cotizacion = self._respaldo("la API del dolar entrego una respuesta inesperada")  # Informa la respuesta rara
            duracion = DURACION_CACHE_FALLO_SEG  # Reintenta en 10 minutos
        except requests.exceptions.RequestException:  # Cualquier otro problema de la petición HTTP
            cotizacion = self._respaldo("fallo la consulta a la API del dolar")  # Informa el problema
            duracion = DURACION_CACHE_FALLO_SEG  # Reintenta en 10 minutos
        DolarService._cache = {"cotizacion": cotizacion, "expira": time.monotonic() + duracion}  # Actualiza la caché
        return cotizacion  # Retorna la cotización obtenida

    def obtener_valor(self) -> float:  # Atajo: solo el número del dólar
        return self.obtener_cotizacion().valor  # Retorna el valor

    # ---------- Métodos internos ----------

    def _obtener_json_desde_api(self) -> dict:  # Hace la petición HTTP real a la API
        respuesta = requests.get(  # Petición GET con la librería requests
            URL_API,  # Dirección fija de la API (no la escribe el usuario)
            headers={"User-Agent": "PowerFit/1.0"},  # Identifica al programa ante el servidor
            timeout=self.__timeout,  # Tiempo máximo de espera: nunca se queda esperando para siempre
        )
        respuesta.raise_for_status()  # Si la API respondió 4xx o 5xx, lanza HTTPError
        return respuesta.json()  # Convierte el JSON a diccionario (ValueError si no es JSON válido)

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

    def _respaldo(self, motivo: str = "") -> Cotizacion:  # Obtiene un valor cuando la API no está disponible
        if self.__conexion is not None:  # Si hay BD...
            guardado = IndicadorDao(self.__conexion).obtener("dolar")  # ...busca el último valor guardado
            if guardado:  # Si existe...
                return Cotizacion(guardado[0], "respaldo", guardado[1][:10], motivo)  # ...lo usa como respaldo y guarda el motivo
        return Cotizacion(VALOR_POR_DEFECTO, "por defecto", "", motivo)  # Último recurso: el valor por defecto
