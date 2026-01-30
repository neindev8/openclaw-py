@echo off
REM ============================================================================
REM MOLTBOT ONE-CLICK SETUP - Instala TODO y ejecuta onboard
REM ============================================================================

chcp 65001 >nul 2>&1
setlocal EnableDelayedExpansion

set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo.
echo ============================================================
echo     MOLTBOT ONE-CLICK SETUP
echo ============================================================
echo.
echo Este script instalara automaticamente:
echo   - Python (si no esta instalado)
echo   - Node.js 22+ (portable si es necesario)
echo   - pnpm (package manager)
echo   - Todas las dependencias del proyecto
echo.
echo Luego ejecutara el wizard de configuracion.
echo.
echo ============================================================
echo.
pause

REM Check Python
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [WARN] Python no encontrado. Instalando via winget...
    winget install -e --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] No se pudo instalar Python automaticamente.
        echo Por favor instala Python 3.8+ desde https://python.org
        pause
        exit /b 1
    )
    echo [INFO] Python instalado. Reinicia este script.
    pause
    exit /b 0
)

echo [OK] Python encontrado

REM Add portable node to PATH
if exist "%SCRIPT_DIR%node_portable" (
    for /d %%d in ("%SCRIPT_DIR%node_portable\node-*") do (
        set "PATH=%%d;%PATH%"
    )
)
set "PATH=%APPDATA%\npm;%PATH%"

REM Run wrapper with auto-onboard flag
python "%SCRIPT_DIR%moltbot_wrapper.py" --auto-onboard

pause
