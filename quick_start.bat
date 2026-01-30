@echo off
REM ============================================================================
REM Quick Start - Runs moltbot onboard directly
REM ============================================================================

chcp 65001 >nul 2>&1
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

echo.
echo [MOLTBOT QUICK START]
echo.

REM Check Node.js
where node >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Node.js not found! Please install Node.js 22+ first.
    pause
    exit /b 1
)

REM Check pnpm
where pnpm >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [INFO] Installing pnpm...
    npm install -g pnpm
)

REM Check if node_modules exists
if not exist "%SCRIPT_DIR%node_modules" (
    echo [INFO] Installing dependencies...
    pnpm install
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b 1
    )
    
    echo [INFO] Building project...
    pnpm build
)

REM Run onboard
echo.
echo [INFO] Starting Moltbot Onboard Wizard...
echo.
pnpm moltbot onboard

pause
