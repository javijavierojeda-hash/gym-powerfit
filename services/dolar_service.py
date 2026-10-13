"""
Servicio que obtiene el valor del dólar del día (requerimiento 6).

Fuente principal: API pública chilena mindicador.cl (datos del Banco Central).
Si esa API no responde, se prueban otras dos APIs públicas del dólar (cl.dolarapi.com
y open.er-api.com): así una caída de un sitio gratuito no deja al programa sin
el valor del día. La consulta usa la librería requests y queda TODA en esta
clase (no repartida por el código). Diseño seguro y tolerante a fallos:
- Timeout corto: si una API no responde, el programa no se queda "colgado".
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
from datetime import datetime, timezone  # Para convertir la fecha de una API que la entrega como número
import requests  # Librería para consumir APIs por HTTP (pip install requests)
from dao.indicador_dao import IndicadorDao  # DAO para guardar/leer el último valor conocido

URL_API = "https://mindicador.cl/api/dolar"  # Dirección de la API principal del dólar
URL_RESPALDO_1 = "https://cl.dolarapi.com/v1/cotizaciones/usd"  # Primera API de respaldo (dólar oficial en Chile)
URL_RESPALDO_2 = "https://open.er-api.com/v6/latest/USD"  # Segunda API de respaldo (tipo de cambio USD -> CLP)
VALOR_POR_DEFECTO = 950.0  # Valor de emergencia si nunca se pudo obtener uno real
RANGO_VALIDO = (100.0, 5000.0)  # Rango de sanidad: un dólar fuera de esto es un dato erróneo
DURACION_CACHE_SEG = 3600  # La cotización obtenida se reutiliza por 1 hora
DURACION_CACHE_FALLO_SEG = 600  # Si la API falló, no se reintenta hasta 10 minutos después


@dataclass(frozen=True)  # frozen=True: el objeto no se puede modificar después de crearlo
class Cotizacion:  # Resultado de consultar el dólar
    valor: float  # Valor del dólar en pesos chilenos
    fuente: str  # De dónde salió: "api", "respaldo" o "por defecto"
    fecha: str  # Fecha del dato
    aviso: str = ""  # Si hubo problemas con alguna API: el motivo, para informarlo al usuario
    origen: str = ""  # Nombre de la API que entregó el valor (ej: "mindicador.cl")


def _validar_valor(valor) -> float:  # Revisa que el dato externo sea un número razonable
    """
    Nunca se confía ciegamente en datos externos: debe ser un número (no un
    texto ni un booleano) dentro de un rango de sanidad.
    """
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):  # Debe ser un número (bool se excluye explícitamente)
        raise ValueError("La API entrego un valor no numerico")  # Rechaza datos extraños
    if not RANGO_VALIDO[0] <= valor <= RANGO_VALIDO[1]:  # Revisa el rango de sanidad
        raise ValueError("La API entrego un valor fuera de rango")  # Rechaza valores absurdos
    return float(valor)  # Retorna el valor validado


def _interpretar_mindicador(datos: dict) -> tuple:  # mindicador.cl: {"serie": [{"fecha": "...", "valor": 950.12}, ...]}
    primero = datos["serie"][0]  # Toma el dato más reciente de la serie
    return _validar_valor(primero["valor"]), str(primero.get("fecha", ""))[:10]  # (valor, fecha)


def _interpretar_dolarapi(datos: dict) -> tuple:  # cl.dolarapi.com: {"compra": 976.0, "venta": 976.4, "fechaActualizacion": "..."}
    return _validar_valor(datos["venta"]), str(datos.get("fechaActualizacion", ""))[:10]  # (valor, fecha)


def _interpretar_er_api(datos: dict) -> tuple:  # open.er-api.com: {"rates": {"CLP": 977.03}, "time_last_update_unix": ...}
    if datos.get("result") != "success":  # La API indica por sí misma si falló
        raise ValueError("La API informo un resultado no exitoso")  # Rechaza la respuesta
    unix = datos.get("time_last_update_unix")  # Fecha de la última actualización (segundos)
    fecha = datetime.fromtimestamp(unix, tz=timezone.utc).date().isoformat() if isinstance(unix, (int, float)) else ""  # A formato AAAA-MM-DD
    return _validar_valor(datos["rates"]["CLP"]), fecha  # (valor, fecha)


@dataclass(frozen=True)  # Una API de dólar: nombre, dirección y cómo leer su respuesta
class Fuente:
    nombre: str  # Nombre que se muestra al usuario
    url: str  # Dirección de la API (fija en el código; no la escribe el usuario)
    interpretar: object  # Función que convierte el JSON de esa API en (valor, fecha)


FUENTES = (  # Orden de consulta: primero mindicador.cl y, si falla, las de respaldo
    Fuente("mindicador.cl", URL_API, _interpretar_mindicador),
    Fuente("cl.dolarapi.com", URL_RESPALDO_1, _interpretar_dolarapi),
    Fuente("open.er-api.com", URL_RESPALDO_2, _interpretar_er_api),
)


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
        self.__obtener_json = obtener_json  # Función de prueba (None = usa la API real); en ese caso solo se consulta la fuente principal
        self.__timeout = timeout  # Guarda el tiempo máximo de espera

    @classmethod
    def limpiar_cache(cls) -> None:  # Borra la caché (útil en pruebas o para forzar una actualización)
        cls._cache = {"cotizacion": None, "expira": 0.0}  # Reinicia la caché

    def obtener_cotizacion(self) -> Cotizacion:  # Método principal: retorna el dólar del día
        cache = DolarService._cache  # Obtiene la caché compartida
        if cache["cotizacion"] and time.monotonic() < cache["expira"]:  # Si hay un valor y no ha expirado...
            return cache["cotizacion"]  # ...lo reutiliza sin llamar a la API
        cotizacion, fallos = None, []  # Resultado y lista de (API, motivo) de las que fallaron
        for fuente in (FUENTES[:1] if self.__obtener_json else FUENTES):  # Prueba cada API en orden hasta que una responda
            try:  # Intenta obtener el valor real desde esta API
                datos = self.__obtener_json() if self.__obtener_json else self._obtener_json_desde_api(fuente.url)  # Descarga y decodifica el JSON
                valor, fecha = fuente.interpretar(datos)  # Extrae y valida el valor
            except requests.exceptions.Timeout:  # La API tardó más que el tiempo máximo de espera
                fallos.append((fuente.nombre, f"la API no respondio en {self.__timeout:.0f} segundos"))  # Informa la demora
            except requests.exceptions.ConnectionError:  # No hay internet o no se encontró el servidor
                fallos.append((fuente.nombre, "no hay conexion con la API (revise internet)"))  # Informa la falta de conexión
            except requests.exceptions.HTTPError as error:  # La API respondió con un error (404, 500, ...)
                codigo = error.response.status_code if error.response is not None else ""  # Código HTTP del error
                fallos.append((fuente.nombre, f"la API respondio con error HTTP {codigo}".strip()))  # Informa el código
            except (ValueError, KeyError, IndexError, TypeError):  # JSON inválido, sin los campos esperados o con un valor que no es número
                fallos.append((fuente.nombre, "la API entrego una respuesta inesperada"))  # Informa la respuesta rara
            except requests.exceptions.RequestException:  # Cualquier otro problema de la petición HTTP
                fallos.append((fuente.nombre, "fallo la consulta a la API"))  # Informa el problema
            else:  # Una API respondió bien: no se prueban las demás
                aviso = "; ".join(f"{n}: {m}" for n, m in fallos)  # Qué APIs anteriores fallaron (si alguna)
                cotizacion = Cotizacion(valor, "api", fecha, f"{aviso}; se uso {fuente.nombre}" if aviso else "", fuente.nombre)  # Valor real
                self._guardar_respaldo(valor)  # Guarda el valor en la BD para usarlo si todas las APIs fallan después
                break  # Termina la búsqueda
        if cotizacion is not None:  # Si alguna API entregó el valor...
            duracion = DURACION_CACHE_SEG  # ...se guarda en caché por 1 hora
        else:  # Si fallaron todas las APIs...
            motivos = {m for _, m in fallos}  # Motivos distintos
            aviso = (f"{motivos.pop()}; se probaron {len(fallos)} fuentes" if len(motivos) == 1 and len(fallos) > 1  # Todas fallaron igual
                     else "; ".join(f"{n}: {m}" for n, m in fallos))  # Fallaron distinto: se detalla cada una
            cotizacion = self._respaldo(aviso)  # ...usa el último valor conocido o el valor por defecto
            duracion = DURACION_CACHE_FALLO_SEG  # ...y reintenta en 10 minutos
        DolarService._cache = {"cotizacion": cotizacion, "expira": time.monotonic() + duracion}  # Actualiza la caché
        return cotizacion  # Retorna la cotización obtenida

    def obtener_valor(self) -> float:  # Atajo: solo el número del dólar
        return self.obtener_cotizacion().valor  # Retorna el valor

    # ---------- Métodos internos ----------

    def _obtener_json_desde_api(self, url: str = URL_API) -> dict:  # Hace la petición HTTP real a la API indicada
        respuesta = requests.get(  # Petición GET con la librería requests
            url,  # Dirección fija de una de las APIs de FUENTES (no la escribe el usuario)
            headers={"User-Agent": "PowerFit/1.0"},  # Identifica al programa ante el servidor
            timeout=self.__timeout,  # Tiempo máximo de espera: nunca se queda esperando para siempre
        )
        respuesta.raise_for_status()  # Si la API respondió 4xx o 5xx, lanza HTTPError
        return respuesta.json()  # Convierte el JSON a diccionario (ValueError si no es JSON válido)

    def _guardar_respaldo(self, valor: float) -> None:  # Guarda el último valor real en la BD
        if self.__conexion is not None:  # Solo si hay una conexión disponible
            IndicadorDao(self.__conexion).guardar("dolar", valor)  # Guarda o reemplaza el valor 'dolar'

    def _respaldo(self, motivo: str = "") -> Cotizacion:  # Obtiene un valor cuando la API no está disponible
        if self.__conexion is not None:  # Si hay BD...
            guardado = IndicadorDao(self.__conexion).obtener("dolar")  # ...busca el último valor guardado
            if guardado:  # Si existe...
                return Cotizacion(guardado[0], "respaldo", guardado[1][:10], motivo)  # ...lo usa como respaldo y guarda el motivo
        return Cotizacion(VALOR_POR_DEFECTO, "por defecto", "", motivo)  # Último recurso: el valor por defecto
