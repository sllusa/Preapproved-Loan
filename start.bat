@echo off
setlocal enabledelayedexpansion

echo === Checking prerequisites ===

:: Check Python 3.10+
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Install from https://python.org
    exit /b 1
)
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYTHON_VER=%%v
echo OK Python %PYTHON_VER%

:: Check Node.js 18+
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js not found. Install from https://nodejs.org
    exit /b 1
)
for /f "tokens=1" %%v in ('node --version') do set NODE_VER=%%v
echo OK Node.js %NODE_VER%

:: Check npm
npm --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: npm not found
    exit /b 1
)
for /f %%v in ('npm --version') do set NPM_VER=%%v
echo OK npm %NPM_VER%
echo.

:: Database — default to SQLite
if not defined DATABASE_URL set DATABASE_URL=sqlite:///./preapproved_loan.db
echo Database: %DATABASE_URL%

:: Find available port for backend (Windows)
set BACKEND_PORT=9000
:find_backend_port
netstat -an | find ":%BACKEND_PORT% " >nul 2>&1
if not errorlevel 1 (
    echo Port %BACKEND_PORT% in use, trying next...
    set /a BACKEND_PORT+=1
    goto find_backend_port
)

:: Find available port for frontend (Windows)
set FRONTEND_PORT=5173
:find_frontend_port
netstat -an | find ":%FRONTEND_PORT% " >nul 2>&1
if not errorlevel 1 (
    echo Port %FRONTEND_PORT% in use, trying next...
    set /a FRONTEND_PORT+=1
    goto find_frontend_port
)

:: === Backend Setup ===
echo.
echo === Setting up backend ===
cd backend

:: Create/activate virtual environment
if not exist ".venv" (
    echo Creating Python virtual environment...
    python -m venv .venv
)
call .venv\Scripts\activate.bat

:: Install dependencies
echo Installing backend dependencies...
if exist "pyproject.toml" (
    pip install . -q
) else if exist "requirements.txt" (
    pip install -r requirements.txt -q
)

:: Run Alembic migrations
if exist "alembic" (
    echo Running database migrations...
    alembic upgrade head 2>nul || echo   Warning: Migration skipped
)

:: Run seed data
echo Seeding database...
if exist "app\seed.py" (
    python -m app.seed 2>nul || echo   Warning: Seed skipped
)

:: Start backend
echo Starting backend on http://localhost:%BACKEND_PORT%
start /b uvicorn app.main:app --host 0.0.0.0 --port %BACKEND_PORT%

:: Capture backend PID
timeout /t 1 /nobreak >nul
for /f "tokens=2" %%p in ('tasklist /fi "imagename eq python.exe" /fo list ^| find "PID:"') do (
    echo %%p > ..\pids.txt
    goto backend_started
)
:backend_started

cd ..

:: === Frontend Setup ===
if exist "frontend\package.json" (
    echo.
    echo === Setting up frontend ===
    cd frontend

    :: Install dependencies
    echo Installing frontend dependencies...
    call npm install --silent

    :: Update .env with backend port
    if not exist ".env" (
        if exist ".env.example" (
            copy .env.example .env >nul
        )
    )
    if exist ".env" (
        powershell -Command "(Get-Content .env) -replace 'VITE_API_URL=.*', 'VITE_API_URL=http://localhost:%BACKEND_PORT%' | Set-Content .env"
    )

    :: Start frontend
    echo Starting frontend on http://localhost:%FRONTEND_PORT%
    start /b npm run dev -- --port %FRONTEND_PORT%

    :: Capture frontend PID
    timeout /t 1 /nobreak >nul
    for /f "tokens=2" %%p in ('tasklist /fi "imagename eq node.exe" /fo list ^| find "PID:"') do (
        echo %%p >> ..\pids.txt
        goto frontend_started
    )
    :frontend_started

    cd ..
)

:: Give services a moment to start
timeout /t 2 /nobreak >nul

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                    Services Running                            ║
echo ╠════════════════════════════════════════════════════════════════╣
echo ║  Backend API:  http://localhost:%BACKEND_PORT%                            ║
echo ║  API Docs:     http://localhost:%BACKEND_PORT%/docs                       ║
if exist "frontend\package.json" echo ║  Frontend UI:  http://localhost:%FRONTEND_PORT%                            ║
echo ╠════════════════════════════════════════════════════════════════╣
echo ║                 Default Credentials                            ║
echo ╠════════════════════════════════════════════════════════════════╣
echo ║  Email:     admin@example.com                                  ║
echo ║  Password:  admin123                                           ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo Press Ctrl+C to stop, or run stop.bat
pause
