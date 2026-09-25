"""
Funciones de validación reutilizables del dominio PowerFit.

Aquí vive el algoritmo del RUT chileno (módulo 11). Lo usan tanto Socio
(método validar_rut() del diagrama UML) como Trabajador, así la regla
existe en un solo lugar y no se duplica.
"""

import re  # Importa expresiones regulares para revisar el formato del texto

# Patrón de un RUT ya limpio: 7 u 8 dígitos, un guion y un dígito verificador (0-9 o K)
_PATRON_RUT = re.compile(r"^\d{7,8}-[\dK]$")  # Se compila una sola vez para reutilizarlo


def limpiar_rut(rut: str) -> str:  # Define la función que deja el RUT en formato estándar
    """
    Normaliza un RUT al formato 12345678-5 (sin puntos, con guion y K mayúscula).

    Acepta entradas como '12.345.678-5', '12345678-5' o '123456785'.
    No valida el dígito verificador, solo ordena el texto.
    """
    if not isinstance(rut, str):  # Si lo recibido no es texto...
        return ""  # ...retorna vacío para que la validación posterior lo rechace
    texto = rut.strip().upper().replace(".", "").replace(" ", "")  # Quita espacios y puntos, y pasa la k a K
    if "-" not in texto and len(texto) >= 2:  # Si viene sin guion (ej: 123456785)...
        texto = f"{texto[:-1]}-{texto[-1]}"  # ...inserta el guion antes del último carácter
    return texto  # Retorna el RUT normalizado


def calcular_dv(cuerpo: str) -> str:  # Define la función que calcula el dígito verificador
    """
    Calcula el dígito verificador de un RUT usando el algoritmo módulo 11.

    Se multiplica cada dígito (de derecha a izquierda) por la serie 2,3,4,5,6,7
    que se repite, se suman los productos y se aplica 11 - (suma % 11).
    """
    suma = 0  # Acumulador de la suma de productos
    multiplicador = 2  # La serie del módulo 11 comienza en 2
    for digito in reversed(cuerpo):  # Recorre los dígitos desde el último hacia el primero
        suma += int(digito) * multiplicador  # Suma el producto del dígito por su multiplicador
        multiplicador = multiplicador + 1 if multiplicador < 7 else 2  # Avanza la serie y vuelve a 2 después del 7
    resto = 11 - (suma % 11)  # Aplica la fórmula del módulo 11
    if resto == 11:  # Si el resultado es 11...
        return "0"  # ...el dígito verificador es 0
    if resto == 10:  # Si el resultado es 10...
        return "K"  # ...el dígito verificador es K
    return str(resto)  # En cualquier otro caso el DV es el número obtenido


def es_rut_valido(rut: str) -> bool:  # Define la función que dice si un RUT es correcto
    """
    Retorna True si el RUT tiene formato correcto y su dígito verificador cuadra.
    """
    limpio = limpiar_rut(rut)  # Primero deja el RUT en formato estándar
    if not _PATRON_RUT.match(limpio):  # Si no calza con el patrón (letras, largo inválido, etc.)...
        return False  # ...el RUT es inválido
    cuerpo, dv = limpio.split("-")  # Separa el número del dígito verificador
    return calcular_dv(cuerpo) == dv  # Es válido solo si el DV calculado coincide con el ingresado


def formatear_rut(rut: str) -> str:  # Define la función que muestra el RUT con puntos
    """
    Devuelve el RUT con puntos para mostrarlo en pantalla: 12.345.678-5.
    """
    limpio = limpiar_rut(rut)  # Normaliza el RUT recibido
    if "-" not in limpio:  # Si no se pudo normalizar...
        return rut  # ...retorna el texto original sin tocarlo
    cuerpo, dv = limpio.split("-")  # Separa número y dígito verificador
    con_puntos = f"{int(cuerpo):,}".replace(",", ".") if cuerpo.isdigit() else cuerpo  # Agrega separador de miles con punto
    return f"{con_puntos}-{dv}"  # Une el número con puntos y el DV
