"""
Clase Suplemento: productos importados que se venden en el mesón.

Se compran en dólares, por eso el precio en pesos se recalcula con el valor
del dólar del día usando actualizar_precio() (requerimiento 6).
"""


class Suplemento:  # Define la clase Suplemento
    """
    Producto importado con precio en USD y su equivalente en CLP.
    """

    def __init__(  # Constructor del suplemento
        self,
        codigo: str,  # Código único del producto (ej: "PROT-01")
        nombre: str,  # Nombre comercial
        stock: int,  # Unidades disponibles
        precio_usd: float,  # Precio de venta en dólares
        precio_clp: int = 0,  # Precio en pesos (0 hasta que se actualice con el dólar)
    ) -> None:
        if not codigo or not codigo.strip():  # El código es obligatorio
            raise ValueError("El codigo del suplemento es obligatorio")  # Rechaza códigos vacíos
        if not nombre or not nombre.strip():  # El nombre es obligatorio
            raise ValueError("El nombre del suplemento es obligatorio")  # Rechaza nombres vacíos
        self.__codigo: str = codigo.strip().upper()  # Guarda el código en mayúsculas y sin espacios
        self.__nombre: str = nombre.strip()  # Guarda el nombre limpio
        self.__stock: int = 0  # Valor inicial; se asigna con el setter para validar
        self.__precio_usd: float = 0.0  # Valor inicial; se asigna con el setter para validar
        self.__precio_clp: int = int(precio_clp)  # Precio en pesos ya calculado (si existe)
        self.stock = stock  # Asigna el stock usando el setter (valida que no sea negativo)
        self.precio_usd = precio_usd  # Asigna el precio usando el setter (valida que sea positivo)

    @property
    def codigo(self) -> str:  # Getter del código (no se puede cambiar)
        return self.__codigo  # Retorna el código

    @property
    def nombre(self) -> str:  # Getter del nombre
        return self.__nombre  # Retorna el nombre

    @property
    def stock(self) -> int:  # Getter del stock
        return self.__stock  # Retorna las unidades disponibles

    @stock.setter
    def stock(self, valor: int) -> None:  # Setter con validación del stock
        if not isinstance(valor, int) or valor < 0:  # El stock no puede ser negativo
            raise ValueError("El stock debe ser un entero mayor o igual a 0")  # Rechaza el valor
        self.__stock = valor  # Guarda el stock válido

    @property
    def precio_usd(self) -> float:  # Getter del precio en dólares
        return self.__precio_usd  # Retorna el precio en USD

    @precio_usd.setter
    def precio_usd(self, valor: float) -> None:  # Setter con validación del precio
        if not isinstance(valor, (int, float)) or valor <= 0:  # El precio debe ser mayor a 0
            raise ValueError("El precio en USD debe ser mayor a 0")  # Rechaza el valor
        self.__precio_usd = float(valor)  # Guarda el precio como decimal

    @property
    def precio_clp(self) -> int:  # Getter del precio en pesos (solo lectura: se calcula)
        return self.__precio_clp  # Retorna el precio en CLP

    def actualizar_precio(self, valor_dolar: float) -> None:  # Método del UML
        """
        Recalcula el precio en pesos: precio_usd x valor del dólar del día.
        """
        if not isinstance(valor_dolar, (int, float)) or valor_dolar <= 0:  # El dólar debe ser un número positivo
            raise ValueError("El valor del dolar debe ser mayor a 0")  # Protege contra datos erróneos de la API
        self.__precio_clp = round(self.__precio_usd * valor_dolar)  # Calcula y redondea a pesos enteros

    def vender(self, cantidad: int) -> int:  # Descuenta stock y retorna el total de la venta
        """
        Vende 'cantidad' unidades y retorna el total en pesos.
        """
        if not isinstance(cantidad, int) or cantidad <= 0:  # La cantidad debe ser positiva
            raise ValueError("La cantidad debe ser mayor a 0")  # Rechaza cantidades inválidas
        if self.__precio_clp <= 0:  # No se puede vender sin precio en pesos
            raise ValueError("Primero se debe actualizar el precio con el dolar del dia")  # Obliga a cotizar
        if cantidad > self.__stock:  # No se puede vender más de lo que hay
            raise ValueError(f"Stock insuficiente: quedan {self.__stock} unidades")  # Informa el stock real
        self.__stock -= cantidad  # Descuenta las unidades vendidas
        return self.__precio_clp * cantidad  # Retorna el total de la venta en pesos

    def __str__(self) -> str:  # Representación en texto
        return f"{self.__nombre} [{self.__codigo}] USD {self.__precio_usd:.2f}"  # Ej: "Proteina Whey [PROT-01] USD 45.00"
