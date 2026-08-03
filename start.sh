#!/bin/bash
# start.sh — Start the Ruralvía Pre-Approved Loan Platform
set -e
trap 'echo "Shutting down..."; [ -f .pids ] && while IFS= read -r pid; do kill "$pid" 2>/dev/null || true; done < .pids; rm -f .pids; exit 0' SIGINT SIGTERM

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Portable sed (macOS + Linux)
portable_sed() {
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "$@"
    else
        sed -i "$@"
    fi
}

# Port detection
find_available_port() {
    local port=$1
    if command -v lsof &>/dev/null; then
        while lsof -iTCP:$port -sTCP:LISTEN -t >/dev/null 2>&1; do
            echo "Port $port in use, trying $((port+1))..." >&2
            port=$((port+1))
        done
    fi
    echo $port
}

# === Prerequisite checks ===
check_prerequisites() {
    local errors=0
    echo "=== Checking prerequisites ==="

    # Python 3.10+
    if command -v python3 &>/dev/null; then
        PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
        PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
        PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
        if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 10 ]); then
            echo "❌ Python 3.10+ required (found $PYTHON_VERSION)"
            errors=$((errors+1))
        else
            echo "✓ Python $PYTHON_VERSION"
        fi
    else
        echo "❌ Python 3 not found. Install from https://python.org"
        errors=$((errors+1))
    fi

    # Node.js 18+
    if command -v node &>/dev/null; then
        NODE_VERSION=$(node --version | sed 's/v//')
        NODE_MAJOR=$(echo $NODE_VERSION | cut -d. -f1)
        if [ "$NODE_MAJOR" -lt 18 ]; then
            echo "❌ Node.js 18+ required (found $NODE_VERSION)"
            errors=$((errors+1))
        else
            echo "✓ Node.js $NODE_VERSION"
        fi
    else
        echo "❌ Node.js not found. Install from https://nodejs.org"
        errors=$((errors+1))
    fi

    # npm
    if ! command -v npm &>/dev/null; then
        echo "❌ npm not found"
        errors=$((errors+1))
    else
        echo "✓ npm $(npm --version)"
    fi

    # pip
    if command -v python3 &>/dev/null && ! python3 -m pip --version &>/dev/null; then
        echo "❌ pip not found. Run: python3 -m ensurepip"
        errors=$((errors+1))
    fi

    if [ $errors -gt 0 ]; then
        echo ""
        echo "❌ $errors prerequisite(s) missing. Please install them and retry."
        exit 1
    fi
    echo ""
}

check_prerequisites

# === Backend Setup ===
BACKEND_DIR="backend"
echo "=== Setting up backend ==="
cd "$BACKEND_DIR"

# Create/activate virtual environment
if [ ! -d ".venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv .venv
fi
source .venv/bin/activate

# Install dependencies
echo "Installing backend dependencies..."
if [ -f "pyproject.toml" ]; then
    pip install . -q
elif [ -f "requirements.txt" ]; then
    pip install -r requirements.txt -q
fi

# Database — default to SQLite, override with DATABASE_URL env var
export DATABASE_URL="${DATABASE_URL:-sqlite:///./preapproved_loan.db}"
echo "  Database: $DATABASE_URL"

# Run Alembic migrations
if [ -d "alembic" ] && command -v alembic &>/dev/null; then
    echo "Running database migrations..."
    alembic upgrade head 2>/dev/null || echo "  ⚠️  Migration skipped (alembic not configured or already up to date)"
fi

# Run seed data
echo "Seeding database..."
if [ -f "app/seed.py" ]; then
    python -m app.seed 2>/dev/null || echo "  ⚠️  Seed skipped (already seeded or error)"
fi

# Detect available port for backend
BACKEND_PORT=$(find_available_port 9000)
echo "Starting backend on http://localhost:$BACKEND_PORT"

# Start backend
uvicorn app.main:app --host 0.0.0.0 --port $BACKEND_PORT &
BACKEND_PID=$!
echo $BACKEND_PID > ../.pids
cd "$SCRIPT_DIR"

# === Frontend Setup ===
FRONTEND_DIR="frontend"
if [ -d "$FRONTEND_DIR" ] && [ -f "$FRONTEND_DIR/package.json" ]; then
    echo ""
    echo "=== Setting up frontend ==="
    cd "$FRONTEND_DIR"

    # Install dependencies
    echo "Installing frontend dependencies..."
    npm install --silent

    # Detect available port for frontend
    FRONTEND_PORT=$(find_available_port 5173)

    # Update frontend .env with actual backend port
    if [ ! -f ".env" ] && [ -f ".env.example" ]; then
        cp .env.example .env
    fi
    if [ -f ".env" ]; then
        portable_sed "s|VITE_API_URL=.*|VITE_API_URL=http://localhost:$BACKEND_PORT|" .env
    fi

    echo "Starting frontend on http://localhost:$FRONTEND_PORT"

    # Start frontend
    npm run dev -- --port $FRONTEND_PORT &
    FE_PID=$!
    echo $FE_PID >> ../.pids
    cd "$SCRIPT_DIR"
fi

# Give services a moment to start
sleep 2

echo ""
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                    Services Running                            ║"
echo "╠════════════════════════════════════════════════════════════════╣"
echo "║  Backend API:  http://localhost:$BACKEND_PORT                            ║"
echo "║  API Docs:     http://localhost:$BACKEND_PORT/docs                       ║"
[ -n "$FRONTEND_PORT" ] && echo "║  Frontend UI:  http://localhost:$FRONTEND_PORT                            ║"
echo "╠════════════════════════════════════════════════════════════════╣"
echo "║                 Default Credentials                            ║"
echo "╠════════════════════════════════════════════════════════════════╣"
echo "║  Email:     admin@example.com                                  ║"
echo "║  Password:  admin123                                           ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for all background processes
wait
