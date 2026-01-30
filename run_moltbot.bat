@echo off
REM ============================================================================
REM MOLTBOT LAUNCHER - FULLY AUTOCONFIGURABLE
REM Installs Python, Node.js, pnpm, everything automatically
REM ============================================================================

chcp 65001 >nul 2>&1
setlocal EnableDelayedExpansion

set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "CYAN=[96m"
set "RESET=[0m"

echo.
echo %CYAN%============================================================%RESET%
echo %CYAN%     MOLTBOT LAUNCHER - Fully Autoconfigurable%RESET%
echo %CYAN%============================================================%RESET%
echo.

REM ============================================================================
REM Check/Install Python
REM ============================================================================

where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo %YELLOW%[WARN] Python not found. Attempting to install...%RESET%
    
    REM Try winget first
    where winget >nul 2>&1
    if %ERRORLEVEL% equ 0 (
        echo %CYAN%[INFO] Installing Python via winget...%RESET%
        winget install -e --id Python.Python.3.12 --accept-source-agreements --accept-package-agreements
        
        REM Refresh PATH
        call refreshenv >nul 2>&1
        
        REM Check again
        where python >nul 2>&1
        if %ERRORLEVEL% equ 0 (
            echo %GREEN%[OK] Python installed!%RESET%
            goto :python_ok
        )
    )
    
    REM Try Microsoft Store version
    echo %CYAN%[INFO] Trying Microsoft Store Python...%RESET%
    start ms-windows-store://pdp/?productid=9NRWMJP3717K
    echo.
    echo %YELLOW%Please install Python from the Microsoft Store window that opened.%RESET%
    echo %YELLOW%After installation, close and reopen this script.%RESET%
    echo.
    pause
    exit /b 1
)

:python_ok
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo %GREEN%[OK] Python %PYVER%%RESET%

REM ============================================================================
REM Check if wrapper exists
REM ============================================================================

if not exist "%SCRIPT_DIR%moltbot_wrapper.py" (
    echo %RED%[ERROR] moltbot_wrapper.py not found!%RESET%
    pause
    exit /b 1
)

REM ============================================================================
REM Add portable Node.js to PATH if exists
REM ============================================================================

if exist "%SCRIPT_DIR%node_portable" (
    for /d %%d in ("%SCRIPT_DIR%node_portable\node-*") do (
        set "PATH=%%d;%PATH%"
    )
)

REM Also add npm global to PATH
set "NPM_GLOBAL=%APPDATA%\npm"
if exist "%NPM_GLOBAL%" (
    set "PATH=%NPM_GLOBAL%;%PATH%"
)

REM ============================================================================
REM Run Python wrapper
REM ============================================================================

echo.
echo %CYAN%Launching Moltbot Wrapper...%RESET%
echo.

python "%SCRIPT_DIR%moltbot_wrapper.py" %*

set EXIT_CODE=%ERRORLEVEL%

if %EXIT_CODE% neq 0 (
    echo.
    echo %YELLOW%Process exited with code %EXIT_CODE%%RESET%
)

pause
exit /b %EXIT_CODE%
