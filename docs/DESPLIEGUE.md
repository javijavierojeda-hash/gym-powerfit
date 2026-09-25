# 🚀 Despliegue

## 1. Servidor local (tu computador)

Requisitos: Python 3.10 o superior.

```bash
git clone https://github.com/javijavierojeda-hash/gym-powerfit.git
cd gym-powerfit
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Mac / Linux
pip install -r requirements.txt
python app.py
```

Abrir **http://localhost:5000**. La primera vez se crea `powerfit.db` con datos de ejemplo.

### Variables de entorno (opcionales)

| Variable | Para qué sirve | Valor por defecto |
|---|---|---|
| `POWERFIT_SECRET_KEY` | Clave que firma la cookie de sesión. **Obligatoria en el hosting** | Aleatoria en cada arranque (se cierran las sesiones al reiniciar) |
| `POWERFIT_DB` | Ruta del archivo de base de datos | `powerfit.db` junto al código |
| `POWERFIT_DEMO` | `1` carga datos de ejemplo si la BD está vacía; `0` no | `1` |
| `POWERFIT_HTTPS` | `1` envía la cookie solo por HTTPS | `0` |
| `POWERFIT_DEBUG` | `1` activa el modo debug de Flask (**nunca en el hosting**) | `0` |

Generar una clave segura:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## 2. Publicar en internet con PythonAnywhere (gratis)

**¿Por qué PythonAnywhere?** Es gratuito, está pensado para Python/Flask y **conserva el archivo SQLite** entre reinicios (otros hostings gratuitos borran el disco).

1. Crear una cuenta en <https://www.pythonanywhere.com> (plan *Beginner*). Tu app quedará en `https://TU_USUARIO.pythonanywhere.com`.
2. Abrir una consola **Bash** y ejecutar:
   ```bash
   git clone https://github.com/javijavierojeda-hash/gym-powerfit.git
   cd gym-powerfit
   python3.11 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   python seed.py
   ```
3. Pestaña **Web** → *Add a new web app* → *Manual configuration* → *Python 3.11*.
4. En **Virtualenv** poner: `/home/TU_USUARIO/gym-powerfit/.venv`
5. Abrir el **WSGI configuration file** y reemplazar todo su contenido por:
   ```python
   import os, sys
   ruta = "/home/TU_USUARIO/gym-powerfit"             # Carpeta del proyecto
   if ruta not in sys.path:
       sys.path.insert(0, ruta)                         # Permite importar los paquetes del proyecto
   os.chdir(ruta)                                        # Directorio de trabajo = proyecto
   os.environ["POWERFIT_SECRET_KEY"] = "PEGA_AQUI_TU_CLAVE_SECRETA"  # Clave generada con secrets.token_hex(32)
   os.environ["POWERFIT_HTTPS"] = "1"                   # Cookie solo por HTTPS
   from app import app as application                   # PythonAnywhere busca la variable "application"
   ```
6. En la sección **Security** activar *Force HTTPS*.
7. Botón **Reload**. Listo: abre `https://TU_USUARIO.pythonanywhere.com`.

### Actualizar después de nuevos commits

```bash
cd ~/gym-powerfit && git pull && source .venv/bin/activate && pip install -r requirements.txt
```

Luego **Reload** en la pestaña Web.

> ⚠️ **Dólar del día en la cuenta gratuita:** PythonAnywhere gratis solo permite salir a internet hacia una lista de sitios permitidos. Si `mindicador.cl` no está en la lista, la app **igual funciona**: usa el valor de respaldo y lo avisa en pantalla ("Valor por defecto"). Se puede pedir que agreguen el sitio a la lista desde su foro, o usar una cuenta pagada.
