@echo off
REM EDR System Setup Script for Windows
REM ====================================
REM 
REM This script automates the setup of the EDR system on Windows.
REM It creates a virtual environment, installs dependencies, and configures the system.
REM
REM Usage: setup.bat [options]
REM   --frontend    Also install frontend dependencies (requires Node.js)
REM   --help        Show this help message

setlocal enabledelayedexpansion

REM Configuration
set "PROJECT_ROOT=%~dp0"
set "VENV_DIR=%PROJECT_ROOT%.venv"
set "BACKEND_DIR=%PROJECT_ROOT%backend"
set "FRONTEND_DIR=%PROJECT_ROOT%frontend"
set "INSTALL_FRONTEND=false"

REM Helper functions
for /f %%A in ('echo prompt $H ^| cmd') do set "BS=%%A"

:parse_args
if "%1"=="" goto end_parse
if "%1"=="--frontend" (
    set "INSTALL_FRONTEND=true"
    shift
    goto parse_args
)
if "%1"=="--help" (
    goto show_help
)
echo Unknown option: %1
goto show_help

:show_help
echo.
echo EDR System Setup Script
echo.
echo Usage: setup.bat [options]
echo.
echo Options:
echo   --frontend    Also install frontend dependencies (requires Node.js)
echo   --help        Show this help message
echo.
echo Examples:
echo   setup.bat                # Setup backend only
echo   setup.bat --frontend     # Setup backend and frontend
echo.
exit /b 0

:end_parse

echo.
echo ============================================================
echo EDR System Setup
echo ============================================================
echo.

REM Check Python version
echo Checking Python version...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] Python not found. Please install Python 3.11 or later.
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set "PYTHON_VERSION=%%i"
echo [OK] Python %PYTHON_VERSION% found
echo.

REM Create virtual environment
echo Setting up virtual environment...
if not exist "%VENV_DIR%" (
    echo Creating virtual environment...
    python -m venv "%VENV_DIR%"
    if %errorlevel% neq 0 (
        echo [X] Failed to create virtual environment
        exit /b 1
    )
) else (
    echo Virtual environment already exists
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call "%VENV_DIR%\Scripts\activate.bat"
if %errorlevel% neq 0 (
    echo [X] Failed to activate virtual environment
    exit /b 1
)
echo [OK] Virtual environment activated
echo.

REM Upgrade pip
echo Upgrading pip, setuptools, and wheel...
python -m pip install --upgrade pip setuptools wheel >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] Failed to upgrade pip
    exit /b 1
)
echo [OK] pip upgraded
echo.

REM Install backend dependencies
echo Installing backend dependencies...
if exist "%BACKEND_DIR%\requirements.txt" (
    python -m pip install -r "%BACKEND_DIR%\requirements.txt"
    if %errorlevel% neq 0 (
        echo [X] Failed to install backend dependencies
        exit /b 1
    )
    echo [OK] Backend dependencies installed
) else (
    echo [X] requirements.txt not found in %BACKEND_DIR%
    exit /b 1
)
echo.

REM Check configuration
echo Validating configuration...
if exist "%BACKEND_DIR%\config\settings.json" (
    echo [OK] settings.json found
) else (
    echo [X] settings.json not found
    exit /b 1
)

if exist "%BACKEND_DIR%\config\rules.json" (
    echo [OK] rules.json found
) else (
    echo [X] rules.json not found
    exit /b 1
)
echo.

REM Install frontend dependencies if requested
if "%INSTALL_FRONTEND%"=="true" (
    echo Installing frontend dependencies...
    
    where node >nul 2>&1
    if %errorlevel% neq 0 (
        echo [!] Node.js not found. Skipping frontend setup.
        echo [!] You can still run the backend: python main.py
    ) else (
        for /f "tokens=*" %%i in ('node --version') do set "NODE_VERSION=%%i"
        echo [OK] Node.js !NODE_VERSION! found
        
        if exist "%FRONTEND_DIR%\package.json" (
            cd /d "%FRONTEND_DIR%"
            call npm install
            if !errorlevel! neq 0 (
                echo [X] Failed to install frontend dependencies
                cd /d "%PROJECT_ROOT%"
                exit /b 1
            )
            cd /d "%PROJECT_ROOT%"
            echo [OK] Frontend dependencies installed
        ) else (
            echo [X] package.json not found in %FRONTEND_DIR%
        )
    )
    echo.
)

REM Print configuration
echo Configuration
echo.
if "%EDR_SESSION_SECRET%"=="" (
    echo [!] EDR_SESSION_SECRET not set. Using default [INSECURE for production!]
    echo [!] To set a secure secret in PowerShell, run:
    echo     $env:EDR_SESSION_SECRET = "your-secret-here"
) else (
    echo [OK] EDR_SESSION_SECRET is set
)
echo.

REM Print next steps
echo ============================================================
echo Setup Complete!
echo ============================================================
echo.
echo Next steps:
echo.
echo 1. (Optional) Set session secret for production:
echo    $env:EDR_SESSION_SECRET = "your-secret-here"
echo.
echo 2. Start the EDR system:
if "%INSTALL_FRONTEND%"=="true" (
    echo    python main.py --frontend
) else (
    echo    python main.py
)
echo.
echo 3. Access the API:
echo    Backend: http://127.0.0.1:8000
echo    Docs: http://127.0.0.1:8000/docs
echo.
if "%INSTALL_FRONTEND%"=="true" (
    echo 4. Access the frontend:
    echo    Frontend: http://localhost:5173
    echo.
)
echo Default credentials:
echo    Email: admin@edr.local
echo    Password: SecurePassword123!
echo.
