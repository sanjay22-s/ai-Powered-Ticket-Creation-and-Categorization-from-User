# AI-Powered Ticket Creation – Agent Dashboard

Production-ready Agent Dashboard for viewing, filtering, and managing tickets.

## Tech Stack

- **Backend:** FastAPI (Python), PostgreSQL, SQLAlchemy, JWT
- **Frontend:** React (Vite + TypeScript), Tailwind CSS, Context API, Axios

## Prerequisites

- Python 3.10+
- Node.js 18+
- PostgreSQL

## 1. Database

Create a database:

```bash
createdb ticketnew
```

Apply schema (optional; the app can create tables via SQLAlchemy):

```bash
psql -d ticketnew -f database/schema.sql
```

## 2. Backend

```bash
cd backend
cp .env.example .env
# Edit .env: set DATABASE_URL and SECRET_KEY
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate   # Linux/Mac
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend: **http://localhost:8000**  
API docs: **http://localhost:8000/docs**

## 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend: **http://localhost:5173**

Use the proxy in `vite.config.ts` so `/api` calls go to the backend (port 8000).

## 4. Seed Dummy Data

From **project root**, with backend dependencies installed:

**Windows (PowerShell):**
```powershell
$env:PYTHONPATH = "backend"
python scripts/seed_data.py
```

**Linux/Mac:**
```bash
PYTHONPATH=backend python scripts/seed_data.py
```

Or from **backend** directory (activate venv first so dependencies are available):
```bash
cd backend
venv\Scripts\activate    # Windows
# source venv/bin/activate   # Linux/Mac
pip install -r requirements.txt   # if not already done
python ../scripts/seed_data.py
```

**Default logins:**

- **Agent:** `agent@example.com` / `agent123`
- **Admin:** `admin@example.com` / `admin123`

## Project Layout

```
ticketnew/
├── backend/
│   └── app/
│       ├── main.py
│       ├── database.py
│       ├── core/         # config, security
│       ├── models/       # User, Ticket, TicketNote
│       ├── schemas/      # Pydantic
│       └── routers/      # auth, tickets, dashboard
├── frontend/
│   └── src/
│       ├── pages/
│       ├── components/
│       ├── services/     # api.ts
│       ├── context/      # AuthContext
│       └── types/
├── database/
│   └── schema.sql
├── scripts/
│   └── seed_data.py
└── README.md
```

## API Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | Login (email, password) |
| GET | `/api/auth/me` | Current user (JWT) |
| GET | `/api/dashboard/stats` | Dashboard counts |
| GET | `/api/tickets` | List tickets (filter, pagination) |
| GET | `/api/tickets/{id}` | Ticket detail + notes |
| PUT | `/api/tickets/{id}` | Update ticket |
| POST | `/api/tickets/{id}/notes` | Add note |
| PUT | `/api/tickets/{id}/assign` | Assign (body: `assigned_to`) |

All except `/auth/login` require header: `Authorization: Bearer <token>`.
