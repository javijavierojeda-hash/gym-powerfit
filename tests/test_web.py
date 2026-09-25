"""
Pruebas de la aplicación web: login, permisos por rol, seguridad y flujos.
"""

from datetime import date  # Para el mes actual
import conectar  # Para revisar la BD de la app de pruebas
from dao.clase_dao import ClaseDao  # Para obtener los ids de las clases
from tests.conftest import iniciar_sesion, token  # Utilidades de las pruebas

MES = date.today().strftime("%Y-%m")  # Mes actual


def ids_de_clases(app) -> dict:  # Diccionario "Yoga lunes 09:00" -> id
    conexion = conectar.crear_conexion(app.config["DATABASE"])  # Abre la BD de la app
    ids = {str(c): c.id for c in ClaseDao(conexion).listar()}  # Arma el diccionario
    conexion.close()  # Cierra la conexión
    return ids  # Lo retorna


# ---------------- Autenticación ----------------

def test_sin_sesion_redirige_al_login(cliente):  # Rutas protegidas
    respuesta = cliente.get("/socios/")  # Página protegida
    assert respuesta.status_code == 302 and "/login" in respuesta.headers["Location"]  # Redirige al login


def test_login_correcto_e_incorrecto(cliente):  # Login
    assert iniciar_sesion(cliente, "22.222.222-2", "mala-clave").status_code == 401  # Clave incorrecta
    assert iniciar_sesion(cliente, "22.222.222-2", "Recepcion123!").status_code == 302  # Clave correcta: redirige al panel


def test_mensaje_de_error_generico(cliente):  # No revela si el RUT existe
    r1 = iniciar_sesion(cliente, "22.222.222-2", "mala-clave")  # RUT existente
    r2 = iniciar_sesion(cliente, "12.345.678-5", "mala-clave")  # RUT que no es trabajador
    assert "RUT o contrasena incorrectos" in r1.text and "RUT o contrasena incorrectos" in r2.text  # Mismo mensaje


def test_bloqueo_por_fuerza_bruta(cliente):  # 5 fallos -> bloqueo
    codigos = [iniciar_sesion(cliente, "11.111.111-1", "x").status_code for _ in range(5)]  # 5 intentos fallidos
    assert codigos == [401] * 5  # Todos rechazados
    assert iniciar_sesion(cliente, "11.111.111-1", "Instructor123!").status_code == 429  # Bloqueado aunque ahora la clave sea correcta


def test_post_sin_token_csrf_es_rechazado(recepcion):  # Protección CSRF
    respuesta = recepcion.post("/socios/nuevo", data={"rut": "11.222.333-9", "nombre": "X"})  # Sin token
    assert respuesta.status_code == 400  # Rechazado


def test_open_redirect_bloqueado(cliente):  # "siguiente" solo acepta rutas internas
    t = token(cliente.get("/login").text)  # Token del login
    r = cliente.post("/login?siguiente=//sitio-malicioso.com", data={"rut": "22.222.222-2", "password": "Recepcion123!", "csrf_token": t})  # Intento de redirigir afuera
    assert r.headers["Location"] == "/"  # Se queda en el sitio


def test_cabeceras_de_seguridad(cliente):  # Cabeceras HTTP
    r = cliente.get("/login")  # Cualquier página
    assert r.headers["X-Frame-Options"] == "DENY"  # Anti-clickjacking
    assert "script-src 'self'" in r.headers["Content-Security-Policy"]  # Solo scripts propios


# ---------------- Permisos por rol (requerimiento 2) ----------------

def test_recepcionista_no_puede_crear_ni_editar_clases(recepcion, app):  # 403 en rutas de instructor
    clase_id = next(iter(ids_de_clases(app).values()))  # Id de una clase cualquiera
    assert recepcion.get("/clases/nueva").status_code == 403  # No puede crear
    assert recepcion.get(f"/clases/{clase_id}/editar").status_code == 403  # No puede editar
    t = token(recepcion.get("/").text)  # Token CSRF válido
    assert recepcion.post("/clases/nueva", data={"tipo": "yoga", "dia": "lunes", "hora": "10:00", "csrf_token": t}).status_code == 403  # Ni por POST directo


def test_instructor_no_accede_a_recepcion(instructor):  # El instructor no cobra ni vende
    for ruta in ("/socios/", "/inscripciones/", "/suplementos/"):  # Rutas de recepción
        assert instructor.get(ruta).status_code == 403  # Prohibido


def test_instructor_solo_edita_sus_clases(instructor, app):  # Dueño de la clase
    ids = ids_de_clases(app)  # Ids de las clases
    assert instructor.get(f"/clases/{ids['Yoga lunes 09:00']}/editar").status_code == 200  # Clase de Camila
    assert instructor.get(f"/clases/{ids['Spinning martes 18:00']}/editar").status_code == 403  # Clase de Diego


def test_instructor_crea_clase(instructor):  # Crear clase
    t = token(instructor.get("/clases/nueva").text)  # Token del formulario
    r = instructor.post("/clases/nueva", data={"tipo": "spinning", "dia": "sabado", "hora": "10:00", "bicicletas": "14", "csrf_token": t}, follow_redirects=True)  # Envía
    assert "Spinning sabado 10:00 creada" in r.text  # Confirmación


# ---------------- Flujos de recepción ----------------

def test_registrar_socio_valida_rut_y_escapa_html(recepcion):  # Requerimiento 3 + XSS
    t = token(recepcion.get("/socios/nuevo").text)  # Token del formulario
    assert recepcion.post("/socios/nuevo", data={"rut": "11.222.333-0", "nombre": "X", "csrf_token": t}).status_code == 400  # DV incorrecto
    r = recepcion.post("/socios/nuevo", data={"rut": "11.222.333-9", "nombre": "<script>alert(1)</script>", "csrf_token": t}, follow_redirects=True)  # Nombre malicioso
    assert "<script>alert(1)</script>" not in r.text and "&lt;script&gt;" in r.text  # Se muestra escapado, no se ejecuta


def test_flujo_inscripcion_cupo_lleno_y_cobro(recepcion, app):  # Requerimientos 4 y 5
    ids = ids_de_clases(app)  # Ids de las clases
    t = token(recepcion.get("/socios/nuevo").text)  # Token CSRF
    recepcion.post("/socios/nuevo", data={"rut": "11.222.333-9", "nombre": "Nuevo Socio", "csrf_token": t})  # Registra socio
    llena = recepcion.post("/inscripciones/nueva", data={  # Intenta reservar una clase llena + otra
        "rut": "11222333-9", "mes": MES, "clases": [ids["Crossfit viernes 18:30"], ids["Yoga lunes 09:00"]], "csrf_token": t})
    assert "cupo maximo" in llena.text and "NO se guardo" in llena.text  # Se rechaza TODA la inscripción
    ok = recepcion.post("/inscripciones/nueva", data={  # Reserva dos clases con cupo
        "rut": "11222333-9", "mes": MES, "clases": [ids["Yoga lunes 09:00"], ids["Spinning martes 18:00"]], "csrf_token": t}, follow_redirects=True)
    assert "2 clase(s)" in ok.text and "$33.000" in ok.text  # Una inscripción con 2 clases: 15.000 + 18.000
    conexion = conectar.crear_conexion(app.config["DATABASE"])  # Revisa la BD
    inscripcion_id = conexion.execute("SELECT id FROM inscripciones_mensuales WHERE socio_rut = '11222333-9'").fetchone()[0]  # Id guardado
    conexion.close()  # Cierra
    cobro = recepcion.post(f"/inscripciones/{inscripcion_id}/cobrar", data={"csrf_token": t}, follow_redirects=True)  # Cobra
    assert "Cobro registrado por $33.000" in cobro.text  # Cobro correcto
    ingreso = recepcion.post("/ingreso/", data={"rut": "11.222.333-9", "csrf_token": t})  # Control de ingreso
    assert "Puede ingresar" in ingreso.text  # Tras pagar, puede entrar


def test_control_de_ingreso_membresia_vencida(recepcion):  # Requerimiento 5
    t = token(recepcion.get("/ingreso/").text)  # Token CSRF
    r = recepcion.post("/ingreso/", data={"rut": "19.283.746-4", "csrf_token": t})  # Socio vencido de los datos demo
    assert "Membresía vencida" in r.text  # Se le niega el ingreso


def test_venta_de_suplementos(recepcion):  # Requerimiento 6
    pagina = recepcion.get("/suplementos/")  # Catálogo
    assert "Valor por defecto" in pagina.text  # Sin internet en pruebas: se informa la fuente del dólar
    t = token(pagina.text)  # Token CSRF
    ok = recepcion.post("/suplementos/vender", data={"codigo": "PROT-01", "cantidad": "2", "csrf_token": t}, follow_redirects=True)  # Venta válida
    assert "Venta registrada: 2 x Proteina Whey" in ok.text  # Confirmación
    agotado = recepcion.post("/suplementos/vender", data={"codigo": "BCAA-01", "cantidad": "1", "csrf_token": t}, follow_redirects=True)  # Producto sin stock
    assert "insuficiente" in agotado.text  # Se rechaza
