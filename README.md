# SWYNEX User Management API

A production-ready RESTful backend service built with **Python**, **FastAPI**, and **SQLAlchemy ORM**. Features PostgreSQL/SQLite persistence, API Key authentication (`X-API-Key` & Bearer token), strict Pydantic payload validation, standardized error handling, pre-packaged sample data seeding, and deployment configurations for **Render**.

---

## 📌 Submission Links

- **GitHub Repository URL:** [https://github.com/subhankarkhatua27/SWYNEX-API-Project-Setup](https://github.com/subhankarkhatua27/SWYNEX-API-Project-Setup)
- **Live Service URL:** `https://swynex-api-project-setup-1.onrender.com/` 
- **Live Interactive API Docs (Swagger UI):** `https://swynex-api-project-setup-1.onrender.com/docs`
- **Live Alternative API Docs (ReDoc):** `https://swynex-api-project-setup-1.onrender.com/redoc`

> **Note on Live Service URL:** Follow the [Render Deployment Guide](#render-deployment-guide) below to deploy this service to Render in just a few minutes. Once deployed, replace `<YOUR-RENDER-APP-NAME>` with your active Render web service subdomain.

---

## Table of Contents

- [Submission Links](#-submission-links)
- [Key Features](#key-features)
- [Project Architecture & Directory Layout](#project-architecture--directory-layout)
- [Environment Configuration](#environment-configuration)
- [Local Setup & Installation](#local-setup--installation)
- [Sample Data & Database Seeding](#sample-data--database-seeding)
- [Render Deployment Guide](#render-deployment-guide)
  - [Method A: 1-Click Blueprint (`render.yaml`)](#method-a-1-click-blueprint-renderyaml)
  - [Method B: Manual Web Service Setup](#method-b-manual-web-service-setup)
- [API Reference & Endpoints](#api-reference--endpoints)
- [Standardized Error Handling](#standardized-error-handling)
- [Authentication & Security](#authentication--security)
- [Testing the API](#testing-the-api)
  - [1. Interactive Swagger UI (`/docs`)](#1-interactive-swagger-ui-docs)
  - [2. Automated Testing with `pytest`](#2-automated-testing-with-pytest)
  - [3. Command-Line Testing with `curl`](#3-command-line-testing-with-curl)
  - [4. Windows PowerShell Testing](#4-windows-powershell-testing)

---

## Key Features

1. **Robust CRUD API:** Full user lifecycle management (Create, Read, List, Update, Delete) backed by SQLAlchemy 2.0 ORM.
2. **Dual Database Support:** Native support for PostgreSQL (`psycopg` v3 driver) in production with connection pooling (`pool_pre_ping=True`) and SQLite for local development/testing.
3. **Render Cloud Compatibility:** Automatic runtime adaptation for Render database connection strings (translating `postgres://` to `postgresql+psycopg://`).
4. **API Key Authentication:** Protected mutating endpoints (`POST`, `PUT`, `DELETE`) guarded via `X-API-Key` header or `Authorization: Bearer <key>` using constant-time comparison (`secrets.compare_digest`).
5. **Strict Input Validation:** Pydantic v2 schemas validating name lengths, whitespace trimming, alphabetic contents, and RFC-compliant normalized emails.
6. **Standardized Error Responses:** Uniform JSON envelope (`status`, `code`, `message`, `details`) across all HTTP status codes (`400`, `401`, `404`, `409`, `422`, `500`).
7. **Cross-Origin Resource Sharing (CORS):** Full CORS middleware support enabling seamless interaction from frontends and browser clients.
8. **Sample Data Seeder:** Bundled sample dataset (`sample_data.json`) with an idempotent CLI script (`python seed_data.py`) and a protected API endpoint (`POST /seed-data`).
9. **Automated Test Suite:** 18 comprehensive unit and integration tests with `pytest` using an isolated in-memory SQLite database.

---

## Project Architecture & Directory Layout

```text
SWYNEX_Intern_Project/
├── Procfile                    # Render / Heroku process declaration
├── README.md                   # Comprehensive repository documentation
├── render.yaml                 # Render Blueprint configuration (Web + PostgreSQL)
├── requirements.txt            # Root Python dependencies
├── runtime.txt                 # Python runtime version for deployment (3.11.9)
├── sample_data.json            # Seed dataset with realistic sample users
├── seed_data.py                # Standalone CLI seeder script
├── .gitignore                  # Git ignore rules (secrets, venv, caches)
│
├── fastapi_project/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── auth.py             # API Key verification & security schemes
│   │   ├── db.py               # Engine, session factory, auto schema init, Render URI handler
│   │   ├── main.py             # FastAPI app, CORS, routes, exception handlers
│   │   ├── seed.py             # Database seeding logic & idempotent functions
│   │   ├── tables.py           # SQLAlchemy User model
│   │   ├── validators.py       # Pydantic models & validation rules
│   │   └── .env                # Local secrets (never committed to git)
│   ├── .env.example            # Environment template for developers
│   ├── .gitignore
│   ├── README.md               # App-specific documentation
│   ├── requirements.txt        # Packaged dependencies
│   └── sample_data.json        # Inner sample data copy
│
└── tests/
    ├── __init__.py
    └── test_api.py             # 18 automated unit and integration tests
```

---

## Environment Configuration

Configuration values are loaded from environment variables or a local `.env` file located in `fastapi_project/app/.env` (or project root).

A template is provided in `fastapi_project/.env.example`:

```env
# Database Connection String
# For SQLite (local development):
DATABASE_URL=sqlite:///./users.db

# For PostgreSQL (production or local Docker):
# DATABASE_URL=postgresql+psycopg://postgres:your_password@localhost/swynex_db

# Master API Key for protected write endpoints
API_KEY=swynex-secret-api-key-2026
```

---

## Local Setup & Installation

### 1. Clone the repository

```bash
git clone https://github.com/subhankarkhatua27/SWYNEX-API-Project-Setup.git
cd SWYNEX_Intern_Project
```

### 2. Create and activate a Python virtual environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure local environment variables

Copy the example environment file:

```bash
# Windows PowerShell:
Copy-Item fastapi_project\.env.example fastapi_project\app\.env

# Linux / macOS:
cp fastapi_project/.env.example fastapi_project/app/.env
```

### 5. Seed initial sample data (Optional)

```bash
python seed_data.py
```

### 6. Run the development server

```bash
uvicorn fastapi_project.app.main:app --reload
```

The application will start at:
- API Root: `http://127.0.0.1:8000/`
- Interactive Swagger UI: `http://127.0.0.1:8000/docs`
- ReDoc Documentation: `http://127.0.0.1:8000/redoc`

---

## Sample Data & Database Seeding

The project comes with pre-configured sample data located in [`sample_data.json`](sample_data.json) featuring realistic user profiles:

```json
[
  {"name": "Alex Mercer", "email": "alex.mercer@example.com"},
  {"name": "Beatriz Santos", "email": "beatriz.santos@example.com"},
  {"name": "Carlos Chen", "email": "carlos.chen@example.com"},
  {"name": "Diana Prince", "email": "diana.prince@example.com"},
  {"name": "Ethan Hunt", "email": "ethan.hunt@example.com"},
  {"name": "Fiona Gallagher", "email": "fiona.gallagher@example.com"}
]
```

### How to Seed Sample Data

You can seed the sample users using any of three methods:

1. **Via CLI Script (Local or Server Shell):**
   ```bash
   python seed_data.py
   ```
2. **Via Protected REST Endpoint (Ideal for Cloud Deployments like Render):**
   Send an authenticated `POST` request to `/seed-data`:
   ```bash
   curl -X POST http://127.0.0.1:8000/seed-data \
     -H "X-API-Key: swynex-secret-api-key-2026"
   ```
   *Response:*
   ```json
   {
     "status": "ok",
     "message": "Sample data seeding complete. Created 6 new user(s).",
     "users_created": 6,
     "total_users": 6
   }
   ```
3. **Via Swagger UI (`/docs`):**
   Authorize with your API key, expand `POST /seed-data`, and click **Execute**.

> **Idempotency Guarantee:** The seeding routine checks for existing email addresses before inserting. If the users already exist, it skips them without raising duplicate key errors.

---

## Render Deployment Guide

[Render](https://render.com) provides free-tier hosting for web services and managed PostgreSQL databases. Deploy using either the automated Blueprint or manual configuration.

### Method A: 1-Click Blueprint (`render.yaml`)

The repository includes a ready-to-deploy [`render.yaml`](render.yaml) specification that provisions both the FastAPI Web Service and a PostgreSQL database.

1. Sign in to your [Render Dashboard](https://dashboard.render.com).
2. Click **New +** > **Blueprint**.
3. Connect your GitHub repository: `https://github.com/subhankarkhatua27/SWYNEX-API-Project-Setup`.
4. Render will parse `render.yaml` and display the services to create:
   - Web Service: `swynex-api`
   - Database: `swynex-db` (PostgreSQL)
5. Click **Apply**.
6. Render builds the service and links `DATABASE_URL` and `API_KEY` automatically.

---

### Method B: Manual Web Service Setup

If you prefer to configure the deployment manually in the Render UI:

#### Step 1: Create a PostgreSQL Database on Render (Optional but Recommended)
1. In the Render Dashboard, click **New +** > **PostgreSQL**.
2. Set Name: `swynex-db`.
3. Set Database Name: `swynex_db`.
4. Set User: `postgres`.
5. Select the **Free** instance type.
6. Click **Create Database**.
7. Once created, copy the **Internal Database URL** (e.g. `postgres://swynex_user:...@dpg-...-a/swynex_db`).

#### Step 2: Create the Web Service
1. In Render Dashboard, click **New +** > **Web Service**.
2. Connect your GitHub repository: `subhankarkhatua27/SWYNEX-API-Project-Setup`.
3. Configure the settings:
   - **Name:** `swynex-api` (or your preferred name)
   - **Region:** Same region as your database (e.g., Oregon or Frankfurt)
   - **Branch:** `main`
   - **Root Directory:** *(leave blank / default)*
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn fastapi_project.app.main:app --host 0.0.0.0 --port $PORT`
   - **Plan:** `Free`

#### Step 3: Add Environment Variables
In the **Environment Variables** section, add:

| Key | Value | Description |
|---|---|---|
| `DATABASE_URL` | `<Your-PostgreSQL-Connection-String>` | Connection string from Step 1 (or omit for SQLite) |
| `API_KEY` | `swynex-secret-api-key-2026` | Secret API key for protected routes |
| `PYTHON_VERSION` | `3.11.9` | Ensures compatible Python runtime |

> **Automatic URL Conversion:** Render database URLs typically begin with `postgres://`. The application's `fastapi_project/app/db.py` automatically converts `postgres://` to `postgresql+psycopg://` at runtime, ensuring compatibility with SQLAlchemy 2.0 and psycopg v3 without manual adjustments.

#### Step 4: Health Check Path
- Scroll down to **Advanced** > **Health Check Path**.
- Set to: `/health-check`.

#### Step 5: Deploy & Verify
1. Click **Create Web Service**.
2. Wait for the build logs to show `Application startup complete`.
3. Copy your live URL (e.g., `https://swynex-api.onrender.com`).
4. Test the deployment:
   - **Root Info:** Visit `https://<YOUR-RENDER-APP-NAME>.onrender.com/`
   - **Health Check:** Visit `https://<YOUR-RENDER-APP-NAME>.onrender.com/health-check`
   - **Interactive Docs:** Visit `https://<YOUR-RENDER-APP-NAME>.onrender.com/docs`
   - **Seed Initial Users:** In Swagger UI, authorize with your `API_KEY` and execute `POST /seed-data`.

---

## API Reference & Endpoints

| Method | Endpoint | Access | Summary | Status |
|---|---|:---:|---|:---:|
| `GET` | `/` | Public | Service metadata & navigation links | `200` |
| `GET` | `/health-check` | Public | Health check / uptime probe | `200` |
| `GET` | `/users` | Public | List all registered users | `200` |
| `GET` | `/users/{user_id}` | Public | Get single user by positive integer ID | `200` |
| `POST` | `/seed-data` | **Protected** | Seed database with sample dataset | `200` |
| `POST` | `/users` | **Protected** | Create a new user | `201` |
| `PUT` | `/users/{user_id}` | **Protected** | Update user fields (partial/full) | `200` |
| `DELETE` | `/users/{user_id}` | **Protected** | Delete user record | `200` |

---

### Request & Response Schemas

#### 1. API Root (`GET /`)
- **Response `200 OK`:**
```json
{
  "name": "SWYNEX User Management API",
  "version": "1.0.0",
  "status": "online",
  "documentation": {
    "swagger_ui": "/docs",
    "redoc": "/redoc",
    "openapi_json": "/openapi.json"
  },
  "endpoints": {
    "root": "GET /",
    "health_check": "GET /health-check",
    "list_users": "GET /users",
    "get_user": "GET /users/{user_id}",
    "create_user": "POST /users (Protected: X-API-Key)",
    "update_user": "PUT /users/{user_id} (Protected: X-API-Key)",
    "delete_user": "DELETE /users/{user_id} (Protected: X-API-Key)",
    "seed_data": "POST /seed-data (Protected: X-API-Key)"
  }
}
```

#### 2. Create User (`POST /users`) — *Protected*
- **Headers:** `X-API-Key: swynex-secret-api-key-2026`, `Content-Type: application/json`
- **Request Body:**
```json
{
  "name": "John Doe",
  "email": "john.doe@example.com"
}
```
- **Response `201 Created`:**
```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john.doe@example.com"
}
```

#### 3. Update User (`PUT /users/{user_id}`) — *Protected*
- **Headers:** `X-API-Key: swynex-secret-api-key-2026`, `Content-Type: application/json`
- **Request Body (partial update supported):**
```json
{
  "name": "Johnathan Doe"
}
```
- **Response `200 OK`:**
```json
{
  "id": 1,
  "name": "Johnathan Doe",
  "email": "john.doe@example.com"
}
```

#### 4. Delete User (`DELETE /users/{user_id}`) — *Protected*
- **Headers:** `X-API-Key: swynex-secret-api-key-2026`
- **Response `200 OK`:**
```json
{
  "message": "User deleted successfully"
}
```

---

## Standardized Error Handling

All error responses across the application conform to a uniform structure:

```json
{
  "status": "error",
  "code": "<MACHINE_READABLE_CODE>",
  "message": "<HUMAN_READABLE_SUMMARY>",
  "details": null
}
```

### Machine-Readable Error Codes

| Status Code | Code String | Cause |
|---|---|---|
| `401 Unauthorized` | `UNAUTHORIZED` | Missing or invalid API key |
| `404 Not Found` | `NOT_FOUND` | User ID does not exist |
| `409 Conflict` | `CONFLICT` | Email address already registered |
| `422 Unprocessable Content` | `VALIDATION_ERROR` | Schema validation failed (empty name, bad email, negative ID) |
| `500 Internal Server Error` | `INTERNAL_SERVER_ERROR` | Unhandled server exception |

#### Example: 422 Validation Error
```json
{
  "status": "error",
  "code": "VALIDATION_ERROR",
  "message": "Input validation failed. Please review the provided fields.",
  "details": [
    {
      "field": "name",
      "message": "Name must be at least 2 non-whitespace characters long."
    },
    {
      "field": "email",
      "message": "value is not a valid email address: The email address is not valid. It must have exactly one @"
    }
  ]
}
```

#### Example: 401 Unauthorized
```json
{
  "status": "error",
  "code": "UNAUTHORIZED",
  "message": "Authentication required. Please provide a valid API key via the 'X-API-Key' header.",
  "details": null
}
```

---

## Authentication & Security

Protected endpoints require the API Key to be passed via either:

1. **Header (Recommended):**
   ```http
   X-API-Key: swynex-secret-api-key-2026
   ```
2. **Bearer Token:**
   ```http
   Authorization: Bearer swynex-secret-api-key-2026
   ```

Validation is performed via `secrets.compare_digest` to prevent timing attacks.

---

## Testing the API

### 1. Interactive Swagger UI (`/docs`)

1. Start the server (`uvicorn fastapi_project.app.main:app --reload`).
2. Open `http://127.0.0.1:8000/docs` in your browser.
3. Click the green **Authorize** button (top right).
4. Enter `swynex-secret-api-key-2026` in `api_key_header_scheme`.
5. Click **Authorize** and then **Close**.
6. Execute requests directly from the UI.

---

### 2. Automated Testing with `pytest`

Run the complete 18-test suite:

```bash
pytest -v
```

**Expected output:**
```text
tests/test_api.py::test_api_root_metadata PASSED                         [  5%]
tests/test_api.py::test_health_check_public_access PASSED                [ 11%]
tests/test_api.py::test_cors_headers_enabled PASSED                      [ 16%]
tests/test_api.py::test_create_user_unauthorized_when_missing_api_key PASSED [ 22%]
tests/test_api.py::test_create_user_unauthorized_when_invalid_api_key PASSED [ 27%]
tests/test_api.py::test_update_user_unauthorized_when_missing_api_key PASSED [ 33%]
tests/test_api.py::test_delete_user_unauthorized_when_missing_api_key PASSED [ 38%]
tests/test_api.py::test_bearer_token_authentication_supported PASSED     [ 44%]
tests/test_api.py::test_payload_validation_empty_body PASSED             [ 50%]
tests/test_api.py::test_payload_validation_invalid_email PASSED          [ 55%]
tests/test_api.py::test_payload_validation_blank_whitespace_name PASSED  [ 61%]
tests/test_api.py::test_payload_validation_name_too_short PASSED         [ 66%]
tests/test_api.py::test_path_parameter_validation_invalid_id PASSED      [ 72%]
tests/test_api.py::test_full_user_crud_flow_with_auth PASSED             [ 77%]
tests/test_api.py::test_duplicate_email_conflict_error PASSED            [ 83%]
tests/test_api.py::test_user_not_found_consistent_error PASSED           [ 88%]
tests/test_api.py::test_seed_sample_data_unauthorized_without_key PASSED [ 94%]
tests/test_api.py::test_seed_sample_data_authorized_and_idempotent PASSED [100%]

======================= 18 passed in 2.16s =======================
```

---

### 3. Command-Line Testing with `curl`

#### Seed Sample Data (Protected)
```bash
curl -i -X POST http://127.0.0.1:8000/seed-data \
  -H "X-API-Key: swynex-secret-api-key-2026"
```

#### List All Users (Public)
```bash
curl -i -X GET http://127.0.0.1:8000/users
```

#### Create a User (Protected)
```bash
curl -i -X POST http://127.0.0.1:8000/users \
  -H "Content-Type: application/json" \
  -H "X-API-Key: swynex-secret-api-key-2026" \
  -d '{"name": "Bruce Wayne", "email": "bruce.wayne@example.com"}'
```

#### Missing API Key Failure (401 Unauthorized)
```bash
curl -i -X POST http://127.0.0.1:8000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Bruce Wayne", "email": "bruce.wayne@example.com"}'
```

#### Invalid Payload Failure (422 Validation Error)
```bash
curl -i -X POST http://127.0.0.1:8000/users \
  -H "Content-Type: application/json" \
  -H "X-API-Key: swynex-secret-api-key-2026" \
  -d '{"name": "   ", "email": "invalid-email"}'
```

---

### 4. Windows PowerShell Testing

```powershell
$headers = @{
    "Content-Type" = "application/json"
    "X-API-Key"    = "swynex-secret-api-key-2026"
}

# 1. Seed sample users
Invoke-RestMethod -Uri "http://127.0.0.1:8000/seed-data" -Method Post -Headers $headers

# 2. List all users
Invoke-RestMethod -Uri "http://127.0.0.1:8000/users" -Method Get

# 3. Create a new user
$body = @{ name = "Peter Parker"; email = "spidey@example.com" } | ConvertTo-Json
$created = Invoke-RestMethod -Uri "http://127.0.0.1:8000/users" -Method Post -Headers $headers -Body $body
$created

# 4. Update the user
$update = @{ name = "Peter Benjamin Parker" } | ConvertTo-Json
Invoke-RestMethod -Uri "http://127.0.0.1:8000/users/$($created.id)" -Method Put -Headers $headers -Body $update

# 5. Delete the user
Invoke-RestMethod -Uri "http://127.0.0.1:8000/users/$($created.id)" -Method Delete -Headers $headers
```

