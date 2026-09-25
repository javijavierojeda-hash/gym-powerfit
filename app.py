"""
Punto de entrada de la aplicación web PowerFit.

Uso local:   python app.py      -> abre http://localhost:5000
Hosting:     el servidor WSGI importa la variable 'app' de este archivo.
"""

import os  # Para leer variables de entorno
from web import create_app  # Fábrica de la aplicación Flask

app = create_app()  # Crea la aplicación (crea tablas y carga datos demo si la BD está vacía)

if __name__ == "__main__":  # Solo cuando se ejecuta directamente con "python app.py"
    modo_debug = os.environ.get("POWERFIT_DEBUG", "0") == "1"  # El modo debug SOLO se activa a propósito (nunca en el hosting)
    app.run(host="127.0.0.1", port=5000, debug=modo_debug)  # Levanta el servidor local de desarrollo
