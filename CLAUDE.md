# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**题小宝 (TiXiaoBao)** - AI-powered question bank generator for K12 education (grades 1-9). Generates math, Chinese, and English exercises using AI (DashScope/Qwen) and rule-based template systems.

## Quick Start

### Backend (FastAPI + SQLite)

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your DASHSCOPE_API_KEY, JWT_SECRET, etc.

# Run database migrations
python -m db.migrations_cli migrate

# Start server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend (React 19 + Vite)

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Deploy to Cloudflare Pages
npm run deploy
```

## Architecture

### Backend Structure (`backend/`)

```
backend/
├── main.py                 # FastAPI app entry point
├── config.py               # Unified config (DB_PATH, JWT, API keys)
├── api/v1/                 # API routes
│   ├── auth.py            # User authentication (OTP + JWT)
│   ├── questions.py       # AI question generation
│   ├── questions_structured.py  # Structured JSON generation
│   ├── history.py         # User history + sharing
│   ├── templates.py       # Template-based generation
│   └── admin.py           # Admin operations
├── services/               # Business logic layer
│   ├── ai/                # Qwen client, vision, data cleaner
│   ├── user/              # User service + store
│   ├── question/          # Question service + stores
│   ├── admin/             # Admin auth + operation logs
│   └── template/          # Template system + generators
├── db/
│   ├── schema.sql         # Full database schema
│   └── migrations/        # Incremental migration scripts
└── data/                  # SQLite database (tixiaobao.db)
```

### Frontend Structure (`frontend/`)

```
frontend/
├── src/
│   ├── App.tsx            # Main app with React Router
│   ├── features/          # Feature modules
│   │   ├── question-generator/
│   │   ├── history/
│   │   └── auth/
│   ├── components/
│   │   ├── questions/     # Question type components
│   │   └── shared/        # Reusable UI components
│   ├── hooks/             # Custom hooks (useMathJax, useToast)
│   ├── api/               # API client modules
│   └── utils/             # Utilities (printUtils, markdownProcessor)
└── public/
```

## Key Technologies

| Layer | Technology |
|-------|------------|
| Backend | FastAPI (Python 3.8+), SQLite, JWT |
| Frontend | React 19, TypeScript, Vite 7 |
| AI | DashScope (Qwen-plus, Qwen-vision) |
| Rendering | MathJax (LaTeX), marked (Markdown) |
| Deployment | Cloudflare Pages (frontend), uvicorn (backend) |

## Core Features

### 1. AI Question Generation
- **Endpoint**: `POST /api/questions/structured`
- Uses Batch system for efficient API calls (10 requests/batch, 3s timeout)
- Supports text prompts and image uploads (vision recognition)
- Returns structured JSON with meta + questions array

### 2. Template-Based Generation
- **Endpoint**: `POST /api/templates/generate`
- Rule-based generators (no AI cost, instant response)
- Generator registry pattern in `services/template/generators/`
- Implemented: number comparison, addition/subtraction, consecutive operations, currency conversion

### 3. Authentication
- OTP email verification (5min expiry, 5 attempts, rate limited)
- JWT tokens (7 days for users, 2hrs for admin)
- Grade selection required for new users

### 4. History & Sharing
- User question records with soft delete
- Share tokens for public links
- Cursor-based pagination

## Testing

```bash
# Backend tests (pytest)
cd backend
python -m pytest tests/

# Frontend - no test framework configured yet
```

## Deployment

### Backend (Production)
```bash
# Use the restart script (includes version check, migrations, health check)
./restart_backend.sh
```

### Frontend (Cloudflare Pages)
```bash
cd frontend
npm run deploy
```

## Environment Variables

### Required (.env)
```bash
DASHSCOPE_API_KEY=sk-xxx          # No default
JWT_SECRET=your-random-secret     # No default, use secrets.token_urlsafe(32)
ADMIN_PASSWORD_HASH=$2b$12$...    # bcrypt hash

SMTP_HOST=smtp.163.com
SMTP_USER=your-email@163.com
SMTP_PASS=your-auth-code
```

See `.env.example` for full list.

## Database Migrations

```bash
# Check status
python -m db.migrations_cli status

# Run pending migrations
python -m db.migrations_cli migrate

# View history
python -m db.migrations_cli history
```

Migrations are stored in `db/migrations/` and tracked in `schema_migrations` table.

## Code Style & Conventions

- **Backend**: PEP 8, type hints encouraged
- **Frontend**: TypeScript strict mode, functional components with hooks
- **Commits**: Conventional Commits format (`feat:`, `fix:`, `refactor:`, etc.)

## Common Tasks

### Add new question type generator
1. Create generator class in `backend/services/template/generators/`
2. Extend `TemplateGenerator` base class
3. Register in `generators/__init__.py`
4. Add migration for template config

### Add new题型 component
1. Create component in `frontend/src/components/questions/`
2. Follow `QuestionRendererProps` interface
3. Register in `QuestionRenderer.tsx`

### Debug AI generation issues
1. Check `backend/logs/` for API logs
2. Verify `DASHSCOPE_API_KEY` in `.env`
3. Check `ai_generation_records` table for error messages
