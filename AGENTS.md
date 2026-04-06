# AGENTS.md — Beauty Salon MVP

## Project Overview

Full-stack beauty salon app: online booking, loyalty system, admin panel, PWA.

- **Backend:** Django 4.2+ + DRF, PostgreSQL/SQLite, Redis, Celery, JWT auth, drf-spectacular (OpenAPI)
- **Frontend:** React 18 + TypeScript + Vite, Tailwind CSS, Redux Toolkit, React Router 6

---

## Commands

### Backend (`cd backend`)

```bash
# Dev server (local)
python manage.py runserver

# Migrations
python manage.py makemigrations
python manage.py migrate

# Load fixtures
python manage.py loaddata fixtures/initial_data.json

# Tests (pytest)
pytest                                    # all tests
pytest --cov=apps                         # with coverage
pytest apps/appointments/tests.py -v      # single file
pytest -k "keyword" -v                    # pattern match

# Integration tests (Django TestClient, not pytest)
python run_tests.py

# Celery worker (separate terminal)
celery -A beauty_backend worker -l info
celery -A beauty_backend beat -l info

# Windows Celery requires eventlet:
pip install eventlet
celery -A beauty_backend worker -l info -P eventlet

# Format / lint
black . && isort .
flake8
pre-commit run --all-files
```

### Frontend (`cd frontend`)

```bash
npm run dev          # Vite dev server (port 5173)
npm run build        # tsc + vite build
npm run preview      # preview production build
npm run lint         # eslint src --ext ts,tsx
npx vitest run       # all tests
npx vitest run src/components/Foo.test.tsx  # single file
npx vitest           # watch mode
```

### Quick Start (Windows)

```bash
# One-command launcher — auto-checks deps, runs migrations, starts both servers
python start.py
```

### Docker

```bash
docker-compose up --build       # PostgreSQL, Redis, backend (gunicorn), celery, celery-beat, frontend, nginx
docker-compose down
docker-compose down -v          # stop + delete volumes (wipes DB)
```

---

## Architecture

### Backend — `backend/`

```
beauty_backend/
  settings/
    base.py       # shared config
    dev.py        # DEBUG=True, SQLite default
    prod.py       # production overrides
  urls.py         # all /api/v1/* routes + /admin/ + /api/docs/
  celery.py       # Celery app, autodiscover_tasks()

apps/
  core/           # Base models, mixins
  services/       # ServiceCategory, Service
  staff/          # Master, MasterService, working_hours, vacations
  clients/        # Client, FavoriteMaster
  appointments/   # Appointment, AppointmentService, slot generation
  reviews/        # Review (rating 1-5, optional photo)
  promotions/     # Promotion, GiftCertificate, BlacklistedClient, Setting
  auth_app/       # Phone-based auth, JWT, SMS
  admin_panel/    # Admin-only API endpoints (dashboard, calendar, reports)
```

### Frontend — `frontend/src/`

```
App.tsx           # All routes defined here
pages/
  HomePage, ServicesPage, ServiceDetailPage, MasterPage
  BookingPage (5-step wizard), PromotionsPage, ContactsPage
  LoginPage, RegisterPage
  ProfilePage, AppointmentsPage, FavoritesPage
  admin/          # Dashboard, Masters, Calendar, Appointments, Services, Promotions, Reports, Blacklist
  master/         # MasterDashboard, MasterAppointments, MasterReviews, MasterSchedule
store/            # Redux slices (authSlice, bookingSlice, etc.)
api/              # Axios client, API service functions
components/       # Layout, ProtectedRoute, AdminRoute, MasterRoute
```

### User Roles & Route Guards

| Role | Guard | Key Routes |
|------|-------|------------|
| Guest | none | `/`, `/services`, `/masters`, `/booking` |
| Client | `<ProtectedRoute>` | `/profile`, `/profile/appointments`, `/profile/favorites` |
| Admin | `<AdminRoute>` (is_staff) | `/admin/*` |
| Master | `<MasterRoute>` | `/master/*` |

---

## Key Configuration Facts

### Backend Settings
- **Settings module:** `beauty_backend.settings.dev` (default for pytest and local dev)
- **Default DB:** SQLite (`db.sqlite3` in project root) — NOT PostgreSQL locally
- **Three settings files:** `base.py` / `dev.py` / `prod.py`
- **Celery app name:** `beauty_backend` (import as `celery -A beauty_backend`)

### Frontend Config
- **Path alias:** `@/` → `src/` (configured in both `tsconfig.json` and `vite.config.ts`)
- **Vite proxy:** `/api`, `/static`, `/admin` → `http://localhost:8000`
  - `/admin` has special bypass: HTML requests are NOT proxied (served by Vite instead)
- **TypeScript:** `noUnusedLocals: false`, `noUnusedParameters: false` — unused imports/params do NOT cause build failures
- **Build order:** `npm run build` runs `tsc` first, then `vite build`

### Ports

| Port | Service |
|------|---------|
| 5173 | React frontend (Vite) |
| 8000 | Django API |
| 80 | Nginx (Docker only) |
| 5432 | PostgreSQL (Docker only) |
| 6379 | Redis (Docker only) |

---

## API

All endpoints under `/api/v1/`. Swagger: `http://localhost:8000/api/docs/swagger/`

### Auth (phone-based)
- `POST /api/v1/auth/login/` — login with phone/email + password → JWT
- `POST /api/v1/auth/register/` — phone registration
- `POST /api/v1/auth/sms/send/` — send SMS code
- `POST /api/v1/auth/token/refresh/` — refresh JWT
- `GET /api/v1/auth/profile/` — current user profile

### Key endpoints
- `GET /api/v1/staff/masters/{id}/slots/?date=YYYY-MM-DD&service_ids=1,2` — available slots
- `POST /api/v1/appointments/guest/` — booking without registration
- `GET /api/v1/admin-panel/dashboard/stats/` — admin dashboard (admin only)
- `GET /api/v1/admin-panel/calendar/?month=4&year=2026` — admin calendar
- `GET /api/v1/admin-panel/reports/sales/?format=xlsx` — export sales to Excel

---

## Testing

### Backend (pytest)
- **Settings:** `DJANGO_SETTINGS_MODULE = beauty_backend.settings.dev`
- **Fixtures** (`backend/conftest.py`): `api_client`, `user`, `admin_user`, `staff_user`, `master_user`, `master`, `category`, `service`, `master_service`, `client`, `future_time`, `appointment`, `completed_appointment`, `review`, `active_promotion`, `setting`
- **Integration tests:** `python run_tests.py` — uses Django TestClient directly (NOT pytest), creates its own test data, tests full API CRUD

### Frontend (Vitest)
- **Config:** `globals: true`, `environment: 'jsdom'`, setup: `src/test/setup.ts`
- **Stack:** Vitest + Testing Library + MSW for API mocking
- **Pattern:** `src/**/*.test.{ts,tsx}`

---

## Business Logic

### Appointment statuses
`pending` → `confirmed` → `completed` | `cancelled_client` | `cancelled_admin` | `no_show`

### Slot generation (`get_available_slots`)
1. Get master's working hours for the day of week
2. Subtract breaks and vacations
3. Sum service durations + buffer (10 min default)
4. Generate slots at 30-min intervals
5. Exclude slots overlapping existing appointments

### Loyalty system
- **Earn:** 5% of completed appointment total → bonus balance
- **Spend:** up to 30% of next appointment cost in bonuses
- **Referrals:** +500 bonus points when referred client completes first appointment

### Celery tasks
- `send_reminders` — hourly, sends SMS reminders 24h before appointments
- `send_bulk_sms` — on-demand mass SMS

---

## Default Credentials

- **Admin:** `admin@example.com` / `admin123`
- **Masters (fixtures):** `+79001234567` (Stylist), `+79007654321` (Cosmetologist)

---

## Gotchas

- **Windows Celery:** requires `eventlet` package and `-P eventlet` flag
- **Default DB is SQLite** — `.env.example` defaults to `DB_ENGINE=django.db.backends.sqlite3`
- **Admin login accepts email** in the `phone` field (e.g., `admin@example.com`)
- **`run_tests.py` is NOT pytest** — it's a standalone script using Django TestClient; must run separately
- **Vite `/admin` proxy bypass** — HTML requests to `/admin` are served by Vite, not proxied to Django. API requests to `/admin/` endpoints still work.
- **`as any` in App.tsx** — `store.dispatch(fetchProfile() as any)` — existing pattern, don't "fix" without understanding why
- **`db.sqlite3` lives in project root** (not in `backend/`)

---

## Quick Reference

| Task | Command | Notes |
|------|---------|-------|
| Run backend dev server | `python manage.py runserver` | In `backend/` directory |
| Apply migrations | `python manage.py migrate` | After changing models |
| Load initial data | `python manage.py loaddata fixtures/initial_data.json` | Only once or when resetting DB |
| Run all backend tests | `pytest` | In `backend/` |
| Run backend tests with coverage | `pytest --cov=apps` | In `backend/` |
| Run single backend test file | `pytest apps/appointments/tests.py -v` | In `backend/` |
| Run integration tests | `python run_tests.py` | In `backend/` |
| Run frontend dev server | `npm run dev` | In `frontend/` |
| Build frontend for production | `npm run build` | In `frontend/` |
| Run all frontend tests | `npx vitest run` | In `frontend/` |
| Run single frontend test file | `npx vitest run src/components/Foo.test.tsx` | In `frontend/` |
| Lint frontend | `npm run lint` | In `frontend/` |
| Start both servers (dev) | `python start.py` | In project root |
| Start Docker stack | `docker-compose up --build` | In project root |
| Stop Docker stack | `docker-compose down` | In project root |
| Stop Docker stack and remove volumes | `docker-compose down -v` | In project root |
| Run Celery worker | `celery -A beauty_backend worker -l info` | In `backend/` or Docker |
| Run Celery beat | `celery -A beauty_backend beat -l info` | In `backend/` or Docker |
| Run Celery worker with eventlet (Windows) | `celery -A beauty_backend worker -l info -P eventlet` | In `backend/` |
| Run pre-commit hooks | `pre-commit run --all-files` | In `backend/` |
| Format code | `black . && isort .` | In `backend/` |
| Lint code | `flake8` | In `backend/` |

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DJANGO_SETTINGS_MODULE` | `beauty_backend.settings.dev` | Django settings module |
| `DATABASE_URL` | `sqlite:///db.sqlite3` (local) | Database connection string |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis broker |
| `CELERY_BROKER_URL` | `redis://localhost:6379/1` | Celery broker |
| `CORS_ALLOWED_ORIGINS` | `http://localhost:5173` | Allowed origins for CORS |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1,backend,nginx` | Django allowed hosts |
| `VITE_API_URL` | `http://localhost:8000/api/v1` | Vite API base URL |

---

## Common Pitfalls

- **Running Celery on Windows**: install `eventlet` and use `-P eventlet` flag.
- **Using SQLite locally**: migrations and loaddata work with SQLite, but Docker uses PostgreSQL. Ensure `DATABASE_URL` points to the correct DB.
- **Vite `/admin` proxy**: HTML requests to `/admin` are served by Vite; API requests to `/admin/` endpoints still go to Django.
- **`start.py` prerequisites**: Requires a Python virtual environment (`venv`) and Node.js/NPM installed.
- **`run_tests.py`**: Not a pytest command; run separately.
- **`as any` in `App.tsx`**: Existing pattern; avoid changing without understanding.
- **`db.sqlite3` location**: Root of repo, not inside `backend/`.

---

## Documentation & Resources

- **Swagger UI**: `http://localhost:8000/api/docs/swagger/`
- **ReDoc**: `http://localhost:8000/api/docs/redoc/`
- **OpenAPI Schema**: `http://localhost:8000/api/schema/`
- **Admin Panel**: `http://localhost:8000/admin/`
- **Frontend PWA**: `http://localhost:5173/`

---

## Notes for Future Sessions

- Keep `AGENTS.md` up-to-date with any new commands or environment changes.
- Avoid adding new dependencies without updating the Dockerfile and `requirements.txt`.
- When adding new tests, ensure they run with `npx vitest run` and `pytest` without flake8 errors.
- For any new feature, remember to update the API docs and Swagger if necessary.

---

## End of File
