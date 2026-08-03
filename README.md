# Ruralvía Pre-Approved Loan Platform

A full-stack digital lending platform for converting pre-approved consumer loan offers into active loans through a unified web/app experience. Built for multi-entity deployment with strict compliance controls, resilient state management, and idempotent financial operations.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Default Credentials](#default-credentials)
- [API Documentation](#api-documentation)
- [Environment Variables](#environment-variables)
- [Development](#development)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## 🎯 Overview

The Ruralvía Pre-Approved Loan Platform enables eligible retail customers to:
- View pre-approved loan offers with real-time expiry tracking
- Simulate loan terms with live instalment/rate/APR calculations
- Select disbursement accounts with operability validation
- Review and acknowledge precontractual documents (SECCI/INE)
- Complete light verification checks (creditworthiness, anti-fraud, AML/PBC)
- Sign with PSD2/SCA strong customer authentication
- Confirm idempotent IRIS booking and disbursement
- View active loan summaries and amortization schedules

**Key Features:**
- **Idempotent financial operations** — no duplicate disbursements
- **State machine enforcement** — guarded lifecycle transitions with audit trail
- **Multi-entity parameterization** — entity-specific product limits, legal modes, languages
- **Cross-channel continuity** — resume journeys between app and web
- **WCAG 2.1 AA accessibility** — keyboard navigation, semantic HTML, ARIA labels
- **Real-time simulation** — French amortization with live instalment updates

---

## 🛠️ Tech Stack

### Backend
- **Language:** Python 3.10+
- **Framework:** FastAPI
- **Database:** SQLite (default) / PostgreSQL (production)
- **ORM:** SQLAlchemy (sync)
- **Authentication:** JWT with bcrypt password hashing
- **Migrations:** Alembic
- **Testing:** pytest

### Frontend
- **Language:** TypeScript
- **Framework:** React 18
- **Build Tool:** Vite
- **Routing:** React Router v6
- **Styling:** Tailwind CSS
- **HTTP Client:** Native fetch with typed API client
- **State Management:** React Context API

### Infrastructure
- **Database:** SQLite (local), PostgreSQL (production)
- **Process Management:** Shell scripts (start.sh/stop.sh) with PID tracking
- **CORS:** Configurable origins via environment variables

---

## 🏗️ Architecture

### Service Modules (Backend)
- **Journey Orchestrator** — Canonical state machine with guarded transitions
- **Offer Service** — Pre-Approval Engine integration with eligibility normalization
- **Simulation Service** — Real-time pricing with French amortization
- **Document Service** — SECCI/INE generation with acknowledgement capture
- **Checks Orchestrator** — Parallel verification (creditworthiness, fraud, AML)
- **Signature Orchestrator** — PSD2/SCA integration with signed-state gates
- **Booking Service** — Idempotent IRIS booking with reconciliation worker
- **Activation Service** — Loan activation with amortization schedule generation
- **Entity Config Service** — Multi-entity parameterization (no code branching)
- **Audit Service** — Immutable event ledger with transactional outbox

### Page Components (Frontend)
- **Offer Landing** — Hero with offer details and expiry notice
- **Simulation** — Amount/term sliders with real-time calculation
- **Account Selection** — Account cards with operability badges
- **Precontractual Review** — Document list with acknowledgement checkboxes
- **Checks Status** — Progress indicators with auto-navigation
- **SCA Signing** — Signature method selection and PSD2 handoff
- **Disbursement Confirmation** — Success hero with booking status
- **Active Loan Summary** — Balance, next payment, quick actions
- **Amortization Schedule** — Monthly/annual installment breakdown

### Data Flow
```
Frontend (React/Vite) → API Client (fetch + JWT)
  ↓
Backend (FastAPI) → Routers → Services → Adapters
  ↓
Database (SQLAlchemy ORM)
  ↓
External Systems (Pre-Approval, IRIS, Verification Services)
```

---

## ✅ Prerequisites

### Required
- **Python 3.10 or higher** — [Download](https://python.org)
- **Node.js 18 or higher** — [Download](https://nodejs.org)
- **npm** (bundled with Node.js)
- **pip** (bundled with Python)

### Optional
- **PostgreSQL 13+** — If not using SQLite (default is SQLite)
- **lsof** (macOS/Linux) or **netstat** (Windows) — For port detection

### Verify Installation
```bash
python3 --version  # Should be 3.10+
node --version     # Should be 18+
npm --version
pip --version
```

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd preapproved-loan
```

### 2. Start All Services (macOS/Linux)
```bash
chmod +x start.sh stop.sh
./start.sh
```

### 3. Start All Services (Windows)
```cmd
start.bat
```

The startup script will:
1. Check prerequisites (Python 3.10+, Node 18+)
2. Create Python virtual environment
3. Install backend dependencies
4. Run database migrations
5. Seed default data (admin user, entity config, sample offers)
6. Start backend on http://localhost:9000
7. Install frontend dependencies
8. Start frontend on http://localhost:5173

### 4. Access the Application

- **Frontend UI:** http://localhost:5173
- **Backend API:** http://localhost:9000
- **API Documentation:** http://localhost:9000/docs (Swagger UI)
- **ReDoc:** http://localhost:9000/redoc

### 5. Stop All Services

**macOS/Linux:**
```bash
./stop.sh
```

**Windows:**
```cmd
stop.bat
```

---

## 🔐 Default Credentials

The seed script creates a default admin user for immediate testing:

| Field    | Value                |
|----------|----------------------|
| Email    | admin@example.com    |
| Password | admin123             |

**⚠️ Security Warning:** Change these credentials in production. Update the seed script (`backend/app/seed.py`) and environment configuration (`SECRET_KEY`) before deployment.

---

## 📚 API Documentation

### Interactive API Docs
- **Swagger UI:** http://localhost:9000/docs
- **ReDoc:** http://localhost:9000/redoc
- **OpenAPI Schema:** http://localhost:9000/openapi.json

### Key Endpoints

#### Authentication
- `POST /api/v1/auth/login` — Login with email/password, returns JWT token

#### Offers
- `GET /api/v1/offers` — List pre-approved offers for authenticated customer
- `GET /api/v1/offers/{offer_id}` — Get offer details

#### Simulation
- `POST /api/v1/preapproved-loans/journeys/{journey_id}/simulation` — Create simulation with amount/term
- `GET /api/v1/simulations/{simulation_id}` — Get simulation details
- `POST /api/v1/simulations/{simulation_id}/confirm` — Confirm simulation

#### Accounts
- `GET /api/v1/accounts` — List eligible disbursement accounts
- `POST /api/v1/accounts/validate` — Validate account operability

#### Documents
- `GET /api/v1/documents` — List available documents (SECCI, contract)
- `POST /api/v1/documents/acknowledge` — Acknowledge document review

#### Verification
- `POST /api/v1/preapproved-loans/journeys/{journey_id}/checks/execute` — Start verification checks
- `GET /api/v1/preapproved-loans/journeys/{journey_id}/checks/status` — Check verification status

#### Signature
- `POST /api/v1/signature/initiate` — Initiate SCA signature session
- `POST /api/v1/signature/callback` — Handle signature provider callback

#### Booking & Activation
- `POST /api/v1/booking/execute` — Execute idempotent IRIS booking
- `GET /api/v1/booking/{booking_id}/status` — Check booking status
- `POST /api/v1/activation/activate` — Activate loan after disbursement

#### Journey
- `GET /api/v1/journey/{journey_id}` — Get journey state
- `GET /api/v1/journey/{journey_id}/history` — Get state transition history

---

## ⚙️ Environment Variables

### Backend Configuration (backend/.env)

| Variable                          | Required | Default                              | Description                                      |
|-----------------------------------|----------|--------------------------------------|--------------------------------------------------|
| `DATABASE_URL`                    | No       | `sqlite:///./preapproved_loan.db`   | Database connection string                       |
| `SECRET_KEY`                      | Yes      | `change-this-...`                    | JWT signing secret (CHANGE IN PRODUCTION)        |
| `DEBUG`                           | No       | `true`                               | Enable debug mode                                |
| `API_PORT`                        | No       | `9000`                               | Backend API port                                 |
| `CORS_ORIGINS`                    | No       | `http://localhost:5173,...`          | Allowed frontend origins (comma-separated)       |
| `JWT_ALGORITHM`                   | No       | `HS256`                              | JWT signing algorithm                            |
| `JWT_EXPIRATION_MINUTES`          | No       | `1440`                               | JWT token lifetime (24 hours)                    |
| `PRE_APPROVAL_ENGINE_URL`         | No       | `http://localhost:8001`              | Pre-Approval Engine endpoint (mock)              |
| `IRIS_API_URL`                    | No       | `http://localhost:8002`              | IRIS Core/Disbursement API endpoint (mock)       |
| `ACCOUNT_VALIDATION_URL`          | No       | `http://localhost:8003`              | Account validation service endpoint (mock)       |
| `DOCUMENT_GENERATION_URL`         | No       | `http://localhost:8004`              | Document generation service endpoint (mock)      |
| `CREDITWORTHINESS_SERVICE_URL`    | No       | `http://localhost:8005`              | Creditworthiness service endpoint (mock)         |
| `FRAUD_SERVICE_URL`               | No       | `http://localhost:8006`              | Anti-fraud service endpoint (mock)               |
| `AML_SERVICE_URL`                 | No       | `http://localhost:8007`              | AML/PBC service endpoint (mock)                  |
| `SCA_SIGNATURE_URL`               | No       | `http://localhost:8008`              | PSD2/SCA signature service endpoint (mock)       |
| `AMORTIZATION_SERVICE_URL`        | No       | `http://localhost:8009`              | Amortization schedule service endpoint (mock)    |
| `SERVICING_CONTEXT_URL`           | No       | `http://localhost:8010`              | Active-loan servicing context endpoint (mock)    |

### Frontend Configuration (frontend/.env)

| Variable         | Required | Default                     | Description                                  |
|------------------|----------|-----------------------------|----------------------------------------------|
| `VITE_API_URL`   | No       | `http://localhost:9000`     | Backend API base URL                         |

### Setup Example Files

Copy `.env.example` to backend and frontend directories:
```bash
cp .env.example backend/.env
cp .env.example frontend/.env
```

Or let the startup script create default `.env` files automatically.

---

## 💻 Development

### Backend Development

#### Manual Backend Startup (without frontend)
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install .
alembic upgrade head
python -m app.seed
uvicorn app.main:app --host 0.0.0.0 --port 9000 --reload
```

#### Run Backend Tests
```bash
cd backend
source .venv/bin/activate
pytest -v
```

#### Run Backend Linter
```bash
cd backend
ruff check app/
```

#### Create Database Migration
```bash
cd backend
alembic revision --autogenerate -m "Description of changes"
alembic upgrade head
```

#### Seed Database Manually
```bash
cd backend
python -m app.seed
```

### Frontend Development

#### Manual Frontend Startup (without backend)
```bash
cd frontend
npm install
npm run dev
```

#### Run Frontend Tests
```bash
cd frontend
npm run test
```

#### Run Frontend Type Check
```bash
cd frontend
npx tsc --noEmit
```

#### Run Frontend Linter
```bash
cd frontend
npx eslint src/
```

#### Build for Production
```bash
cd frontend
npm run build
# Output: dist/
```

---

## 🐛 Troubleshooting

### Problem: Port Already in Use

**Symptom:** `Port 9000 in use, trying 9001...` or service fails to start

**Solution:**
- The startup script automatically detects and uses the next available port
- Check `.pids` file for running services: `cat .pids`
- Stop services properly: `./stop.sh` (macOS/Linux) or `stop.bat` (Windows)
- Manually kill processes if needed:
  ```bash
  # macOS/Linux
  lsof -i :9000
  kill <PID>
  
  # Windows
  netstat -ano | findstr :9000
  taskkill /PID <PID> /F
  ```

### Problem: Database Connection Error

**Symptom:** `sqlalchemy.exc.OperationalError: unable to open database file`

**Solution:**
- Ensure database directory exists: `mkdir -p backend/`
- Check `DATABASE_URL` in `backend/.env` points to writable location
- Default SQLite path: `backend/preapproved_loan.db`
- For PostgreSQL: verify connection string format and database exists

### Problem: Frontend Cannot Reach Backend

**Symptom:** API calls return 404 or network errors in browser console

**Solution:**
- Verify backend is running: `curl http://localhost:9000/health`
- Check `VITE_API_URL` in `frontend/.env` matches backend port
- Check CORS origins in `backend/.env` include frontend URL
- Restart services after changing environment variables

### Problem: Migration Fails

**Symptom:** `alembic upgrade head` returns error

**Solution:**
- Check database file permissions (SQLite)
- Verify database connection (PostgreSQL)
- Drop database and recreate:
  ```bash
  rm backend/preapproved_loan.db
  cd backend && alembic upgrade head
  python -m app.seed
  ```

### Problem: Seed Script Fails

**Symptom:** `python -m app.seed` returns error

**Solution:**
- Run migrations first: `cd backend && alembic upgrade head`
- Check database connection in `backend/.env`
- Seed is idempotent — safe to run multiple times
- Check for unique constraint violations if manually adding data

### Problem: Virtual Environment Activation Fails (Windows)

**Symptom:** `Execution of scripts is disabled on this system`

**Solution:**
- Enable script execution (run as Administrator):
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```
- Or use batch activation: `call backend\.venv\Scripts\activate.bat`

### Problem: JWT Token Expired / 401 Unauthorized

**Symptom:** Frontend redirects to login after some time

**Solution:**
- JWT tokens expire after 24 hours by default
- Log in again with `admin@example.com` / `admin123`
- Adjust `JWT_EXPIRATION_MINUTES` in `backend/.env` if needed
- Check browser localStorage for `access_token` persistence

### Problem: Frontend Build Fails with TypeScript Errors

**Symptom:** `npm run build` returns type errors

**Solution:**
- Run type check to identify issues: `npx tsc --noEmit`
- Verify all required files exist (especially `src/vite-env.d.ts`)
- Check `tsconfig.json` includes `"noUnusedLocals": false`
- Clear node_modules and reinstall: `rm -rf node_modules && npm install`

---

## 📝 License

Copyright © 2026 Ruralvía. All rights reserved.

This software is provided for demonstration and development purposes.

---

## 🤝 Contributing

This is a demonstration project generated from design specifications. For production deployment:
1. Replace mock external service URLs with real endpoints
2. Change `SECRET_KEY` to a secure random value
3. Use PostgreSQL instead of SQLite
4. Enable HTTPS with valid certificates
5. Implement production-grade logging and monitoring
6. Review and update CORS origins
7. Change seed user credentials or disable seed script

---

## 📞 Support

For questions, issues, or feedback:
- **API Documentation:** http://localhost:9000/docs
- **Frontend:** http://localhost:5173
- **Backend Health Check:** http://localhost:9000/health

**Development Stack:**
- Backend: Python 3.10+ / FastAPI
- Frontend: Node.js 18+ / React 18 / TypeScript / Vite
- Database: SQLite (default) / PostgreSQL
