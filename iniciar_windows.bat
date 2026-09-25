@echo off
REM =====================================================================
REM  PowerFit - Instalador y lanzador para Windows (doble clic)
REM  1. Revisa si Python esta instalado; si no, lo instala con winget.
REM  2. Crea el entorno virtual e instala las dependencias (solo la 1a vez).
REM  3. Levanta la app y abre el navegador en http://localhost:5000
REM =====================================================================
chcp 65001 >nul
title PowerFit
cd /d "%~dp0"

echo.
echo  ==============================================
echo    PowerFit - preparando el sistema...
echo  ==============================================
echo.

REM ---------- 1. Buscar Python (primero el lanzador "py", luego "python") ----------
set "PY="
py -3 --version >nul 2>&1 && set "PY=py -3"
if not defined PY (
    python --version >nul 2>&1 && set "PY=python"
)

if not defined PY (
    echo  [1/3] Python no esta instalado. Instalando con winget...
    winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
    if errorlevel 1 (
        echo.
        echo  No se pudo instalar automaticamente.
        echo  Instala Python desde https://www.python.org/downloads/
        echo  marcando "Add Python to PATH", y vuelve a abrir este archivo.
        pause
        exit /b 1
    )
    echo.
    echo  Python quedo instalado. CIERRA esta ventana y vuelve a abrir
    echo  iniciar_windows.bat para continuar.
    pause
    exit /b 0
)
echo  [1/3] Python encontrado:
%PY% --version

REM ---------- 2. Entorno virtual + dependencias (solo la primera vez) ----------
if not exist ".venv\Scripts\python.exe" (
    echo  [2/3] Creando entorno virtual e instalando dependencias...
    %PY% -m venv .venv || (echo  Error creando el entorno virtual & pause & exit /b 1)
    ".venv\Scripts\python.exe" -m pip install --upgrade pip >nul
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt || (echo  Error instalando dependencias & pause & exit /b 1)
) else (
    echo  [2/3] Dependencias ya instaladas.
)

REM ---------- 3. Abrir el navegador y levantar la app ----------
echo  [3/3] Iniciando PowerFit en http://localhost:5000
echo.
echo    Recepcionista: 22.222.222-2  /  Recepcion123!
echo    Instructora:   11.111.111-1  /  Instructor123!
echo.
echo    Para detener el servidor cierra esta ventana o presiona Ctrl+C.
echo.
start "" /min cmd /c "timeout /t 3 >nul & start http://localhost:5000"
".venv\Scripts\python.exe" app.py
pause
