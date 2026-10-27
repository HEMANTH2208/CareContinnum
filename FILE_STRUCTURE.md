# CareContinuum - Complete File Structure

```
carecontinuum/
├── .dockerignore                  # Docker ignore patterns
├── .gitignore                     # Git ignore patterns
├── docker-compose.yml             # Multi-container orchestration
├── LICENSE                        # MIT License with healthcare notice
├── README.md                      # Main project documentation
├── QUICK_START.md                 # 5-minute setup guide
├── SETUP_GUIDE.md                 # Detailed installation instructions
├── WORKFLOW_DEMO.md               # Complete workflow demonstration
├── PROJECT_SUMMARY.md             # Comprehensive project overview
├── setup.sh                       # Linux/Mac setup script
├── setup.bat                      # Windows setup script
│
├── backend/                       # FastAPI Backend
│   ├── Dockerfile                 # Backend container definition
│   ├── requirements.txt           # Python dependencies
│   ├── .env.example               # Environment template
│   ├── alembic.ini                # Database migration config
│   ├── pytest.ini                 # Test configuration
│   │
│   ├── alembic/                   # Database Migrations
│   │   ├── env.py                 # Migration environment
│   │   ├── script.py.mako         # Migration template
│   │   └── versions/              # Migration versions (auto-generated)
│   │
│   ├── app/                       # Main Application
│   │   ├── __init__.py
│   │   ├── main.py                # FastAPI entry point
│   │   │
│   │   ├── core/                  # Core Utilities
│   │   │   ├── __init__.py
│   │   │   ├── config.py          # Configuration settings
│   │   │   ├── database.py        # Database connection
│   │   │   ├── security.py        # Auth & password hashing
│   │   │   └── dependencies.py    # FastAPI dependencies & RBAC
│   │   │
│   │   ├── models/                # SQLAlchemy Models
│   │   │   ├── __init__.py
│   │   │   ├── user.py            # User & roles
│   │   │   ├── patient.py         # Patient records
│   │   │   ├── appointment.py     # Appointments
│   │   │   ├── follow_up.py       # Follow-up plans & tasks
│   │   │   ├── consultation.py    # Consultations & prescriptions
│   │   │   ├── notification.py    # Notifications & attempts
│   │   │   └── audit.py           # Audit logs
│   │   │
│   │   ├── schemas/               # Pydantic Schemas
│   │   │   ├── __init__.py
│   │   │   ├── user.py            # User validation schemas
│   │   │   ├── patient.py         # Patient schemas
│   │   │   ├── appointment.py     # Appointment schemas
│   │   │   ├── follow_up.py       # Follow-up schemas
│   │   │   └── consultation.py    # Consultation & prescription schemas
│   │   │
│   │   ├── api/                   # API Routes
│   │   │   ├── __init__.py        # Router aggregation
│   │   │   ├── auth.py            # Authentication endpoints
│   │   │   ├── users.py           # User management
│   │   │   ├── patients.py        # Patient CRUD & timeline
│   │   │   ├── appointments.py    # Appointment management
│   │   │   ├── follow_ups.py      # Follow-up plans & worklist
│   │   │   ├── consultations.py   # Consultations & prescriptions
│   │   │   └── analytics.py       # Dashboard & metrics
│   │   │
│   │   └── services/              # Business Logic
│   │       ├── __init__.py
│   │       ├── ai_service.py      # AI summaries & task extraction
│   │       ├── notification_service.py  # Multi-channel notifications
│   │       ├── prescription_service.py  # PDF generation
│   │       ├── scheduler.py       # Background job scheduler
│   │       └── seed_data.py       # Database seeding script
│   │
│   └── tests/                     # Backend Tests
│       ├── __init__.py
│       ├── test_auth.py           # Authentication tests
│       └── test_patients.py       # Patient API tests
│
├── frontend/                      # React Frontend
│   ├── Dockerfile                 # Frontend container definition
│   ├── package.json               # NPM dependencies & scripts
│   ├── tsconfig.json              # TypeScript configuration
│   ├── tsconfig.node.json         # Node TypeScript config
│   ├── vite.config.ts             # Vite build configuration
│   ├── tailwind.config.js         # Tailwind CSS config
│   ├── postcss.config.js          # PostCSS configuration
│   ├── .eslintrc.cjs              # ESLint configuration
│   ├── .gitignore                 # Frontend-specific ignores
│   ├── index.html                 # HTML entry point
│   │
│   ├── public/                    # Static Assets
│   │   └── vite.svg               # Vite logo
│   │
│   └── src/                       # Source Code
│       ├── main.tsx               # React entry point
│       ├── App.tsx                # Main app component
│       ├── index.css              # Global styles & Tailwind
│       │
│       ├── types/                 # TypeScript Types
│       │   └── index.ts           # Shared type definitions
│       │
│       ├── contexts/              # React Contexts
│       │   └── AuthContext.tsx    # Authentication context
│       │
│       ├── services/              # API Services
│       │   └── api.ts             # Axios client & API functions
│       │
│       ├── components/            # Reusable Components
│       │   └── layouts/
│       │       └── DashboardLayout.tsx  # Main layout with sidebar
│       │
│       └── pages/                 # Page Components
│           ├── LoginPage.tsx      # Login form
│           ├── DashboardPage.tsx  # Main dashboard
│           ├── PatientsPage.tsx   # Patient list
│           ├── PatientDetailPage.tsx  # Patient timeline
│           ├── AppointmentsPage.tsx   # Appointment management
│           ├── WorklistPage.tsx   # Priority worklist
│           ├── UsersPage.tsx      # User management (admin)
│           └── AnalyticsPage.tsx  # Analytics dashboard
│
└── prescriptions/                 # Generated PDFs (created at runtime)
    └── prescription_*.pdf         # Prescription PDF files
```

## File Count Summary

- **Backend Files**: 40+
- **Frontend Files**: 25+
- **Documentation Files**: 6
- **Configuration Files**: 15+
- **Total**: 86+ files

## Key Directories Explained

### Backend Core (`backend/app/core/`)
Configuration, database connection, security utilities, and dependency injection.

### Backend Models (`backend/app/models/`)
SQLAlchemy ORM models defining database schema.

### Backend Schemas (`backend/app/schemas/`)
Pydantic models for request/response validation.

### Backend API (`backend/app/api/`)
FastAPI route handlers organized by resource.

### Backend Services (`backend/app/services/`)
Business logic layer for complex operations.

### Frontend Services (`frontend/src/services/`)
API client functions using Axios.

### Frontend Pages (`frontend/src/pages/`)
Main page components for different routes.

### Frontend Components (`frontend/src/components/`)
Reusable UI components (layouts, forms, etc.).

## Generated at Runtime

- `backend/alembic/versions/*.py` - Migration files
- `prescriptions/*.pdf` - Prescription PDFs
- `backend/*.db` - SQLite test databases
- `node_modules/` - NPM packages
- `backend/venv/` - Python virtual environment
- `frontend/dist/` - Production build
- `backend/__pycache__/` - Python bytecode

## Environment Files (Not in Git)

- `backend/.env` - Backend configuration
- `frontend/.env` - Frontend configuration

## Docker Volumes

- `postgres_data` - PostgreSQL database files
- `redis_data` - Redis persistence (if configured)

## Notable Patterns

- **Separation of Concerns**: Models, schemas, services, and routes are clearly separated
- **Dependency Injection**: FastAPI dependencies for database sessions and auth
- **Type Safety**: TypeScript on frontend, Pydantic on backend
- **Consistent Naming**: Clear, descriptive file and function names
- **Modular Structure**: Easy to locate and modify specific functionality
