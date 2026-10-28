# SWYNEX Intern Project

A production-grade backend service built with Python and FastAPI. The API features user management (CRUD) backed by SQLAlchemy ORM and PostgreSQL (with SQLite compatibility), protected routes using API Key authentication, strict incoming payload validation with Pydantic, and consistent standardized error responses across all failure scenarios.

---

## Table of Contents

- [Project Structure](#project-structure)
- [Requirements](#requirements)
- [Setup & Installation](#setup--installation)
- [Environment Configuration](#environment-configuration)
- [Running the Application](#running-the-application)
- [Authentication & Protected Routes](#authentication--protected-routes)
- [Incoming Payload Validation](#incoming-payload-validation)
- [Standardized Error Responses](#standardized-error-responses)
- [API Endpoints Overview](#api-endpoints-overview)
- [How to Test the Protected Routes](#how-to-test-the-protected-routes)
  - [Method 1: Interactive Swagger UI (`/docs`)](#method-1-interactive-swagger-ui-docs)
  - [Method 2: Command Line Testing with `curl`](#method-2-command-line-testing-with-curl)
  - [Method 3: PowerShell Testing with `Invoke-RestMethod`](#method-3-powershell-testing-with-invoke-restmethod)
  - [Method 4: Automated Test Suite with `pytest`](#method-4-automated-test-suite-with-pytest)
- [Interactive API Documentation](#interactive-api-documentation)

---

## Project Structure

```text
SWYNEX_Intern_Project/
│
├── .venv/                      # Local Python virtual environment (ignored in git)
├── tests/                      # Automated test suite
│   ├── __init__.py
│   └── test_api.py             # 14 unit & integration test cases
│
├── fastapi_project/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── auth.py             # API Key authentication dependency (X-API-Key / Bearer)
│   │   ├── db.py               # Database engine, sessionmaker, and session dependency
│   │   ├── main.py             # FastAPI app, exception handlers, and API routes
│   │   ├── tables.py           # SQLAlchemy ORM User model
│   │   ├── validators.py       # Pydantic schemas, payload validators, error models
│   │   └── .env                # Local secrets (not committed to git)
│   │
│   ├── .env.example            # Sample environment variables template
│   ├── .gitignore
│   ├── README.md
│   └── requirements.txt        # Project dependencies
└── .gitignore
```

---

## Requirements

- **Python 3.10+** (Python 3.10, 3.11, 3.12, 3.13, or 3.14)
- **pip** package installer
- **Git**

---

## Setup & Installation

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd SWYNEX_Intern_Project
```

### 2. Create and activate a virtual environment

**Windows PowerShell:**
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

When activated, your terminal prompt will show `(.venv)`.

### 3. Install dependencies

```bash
pip install -r fastapi_project/requirements.txt
```

---

## Environment Configuration

Configuration is managed via a `.env` file located in `fastapi_project/app/.env` (or project root). A template is provided in `fastapi_project/.env.example`.

Create or edit `fastapi_project/app/.env`:

```env
# Database connection string (PostgreSQL or SQLite)
DATABASE_URL="postgresql+psycopg://postgres:your_password@localhost/swynex_db"
# Or for local SQLite:
# DATABASE_URL="sqlite:///./users.db"

# Master API Key for protected endpoints
API_KEY="swynex-secret-api-key-2026"
```

> **Security Note:** Never commit `.env` containing sensitive credentials to GitHub. The `.gitignore` file is configured to exclude all `.env` files.

---

## Running the Application

From the repository root `SWYNEX_Intern_Project`:

```bash
uvicorn fastapi_project.app.main:app --reload
```

The API service will start at:
```
http://127.0.0.1:8000
```

---

## Authentication & Protected Routes

Write operations and sensitive endpoints are protected with API Key authentication:

- **Protected Endpoints:**
  - `POST /users` (Create new user)
  - `PUT /users/{user_id}` (Update existing user)
  - `DELETE /users/{user_id}` (Delete user)
- **Public Endpoints:**
  - `GET /health-check` (System health probe)
  - `GET /users` (List all users)
  - `GET /users/{user_id}` (View user details)

### How Authentication Works

Clients authenticate by supplying the API key in either of two standard header formats:

1. **Header (Recommended):**
   ```http
   X-API-Key: swynex-secret-api-key-2026
   ```
2. **Bearer Token (Alternative):**
   ```http
   Authorization: Bearer swynex-secret-api-key-2026
   ```

Authentication is validated using constant-time comparison (`secrets.compare_digest`) to prevent timing attacks. If the key is missing or invalid, the API returns a consistent `401 UNAUTHORIZED` error response.

---

## Incoming Payload Validation

All request payloads are strictly validated using Pydantic schemas in `app/validators.py`:

### 1. User Creation (`POST /users`) — `UserRequest`

| Field | Type | Rules | Example |
|---|---|---|---|
| `name` | string | Required, 2–100 characters, automatically trimmed of whitespace, must contain alphabetic characters. Cannot be blank. | `"John Doe"` |
| `email` | string (EmailStr) | Required, valid RFC email address, normalized to lowercase, max 255 chars. | `"john.doe@example.com"` |

### 2. User Update (`PUT /users/{user_id}`) — `UserUpdateRequest`

| Field | Type | Rules | Example |
|---|---|---|---|
| `name` | string | Optional, 2–100 characters if supplied. | `"Jane Doe"` |
| `email` | string (EmailStr) | Optional, valid RFC email address if supplied. | `"jane.doe@example.com"` |

*Note:* At least one field (`name` or `email`) must be provided in the update payload.

### 3. Path Parameters (`user_id`)

The `user_id` path parameter is constrained to positive integers (`user_id > 0`). Non-positive IDs return a validation error.

---

## Standardized Error Responses

Every error across the entire application—whether from authentication failure, invalid payload, database conflict, missing resource, or server error—returns a consistent JSON envelope:

```json
{
  "status": "error",
  "code": "<MACHINE_READABLE_CODE>",
  "message": "<HUMAN_READABLE_MESSAGE>",
  "details": null
}
```

### Error Code Reference

| Status Code | Code String | Trigger Scenario |
|---|---|---|
| **401 Unauthorized** | `UNAUTHORIZED` | Missing or invalid `X-API-Key` header on protected endpoints. |
| **403 Forbidden** | `FORBIDDEN` | Access forbidden. |
| **404 Not Found** | `NOT_FOUND` | User ID does not exist in the database. |
| **409 Conflict** | `CONFLICT` | Attempt to register or update to an email address that already exists. |
| **422 Unprocessable Content** | `VALIDATION_ERROR` | Missing required fields, invalid email format, empty whitespace name, or non-positive ID. |
| **500 Internal Server Error** | `INTERNAL_SERVER_ERROR` | Unhandled server exception. |

### Error Response Examples

#### 1. Unauthorized (401)
```json
{
  "status": "error",
  "code": "UNAUTHORIZED",
  "message": "Authentication required. Please provide a valid API key via the 'X-API-Key' header.",
  "details": null
}
```

#### 2. Validation Error (422)
When fields fail validation, the `details` array provides exact field-level diagnostics:
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

#### 3. Duplicate Email Conflict (409)
```json
{
  "status": "error",
  "code": "CONFLICT",
  "message": "A user with email 'john.doe@example.com' already exists.",
  "details": null
}
```

#### 4. Resource Not Found (404)
```json
{
  "status": "error",
  "code": "NOT_FOUND",
  "message": "User with ID 999 not found",
  "details": null
}
```

---

## API Endpoints Overview

| Method | Endpoint | Auth Required | Description |
|---|---|:---:|---|
| `GET` | `/health-check` | No | System health check |
| `GET` | `/users` | No | List all users |
| `GET` | `/users/{user_id}` | No | Get user details by ID |
| `POST` | `/users` | **Yes (`X-API-Key`)** | Create a new user (Status 201) |
| `PUT` | `/users/{user_id}` | **Yes (`X-API-Key`)** | Update user details (Status 200) |
| `DELETE` | `/users/{user_id}` | **Yes (`X-API-Key`)** | Delete user record (Status 200) |

---

## How to Test the Protected Routes

### Method 1: Interactive Swagger UI (`/docs`)

1. Start the API server:
   ```bash
   uvicorn fastapi_project.app.main:app --reload
   ```
2. Open your browser and navigate to:
   ```
   http://127.0.0.1:8000/docs
   ```
3. Click the green **Authorize** (padlock) button at the top-right of the page.
4. In the dialog, enter your API key under `api_key_header_scheme`:
   ```
   swynex-secret-api-key-2026
   ```
5. Click **Authorize**, then **Close**.
6. Expand `POST /users`, click **Try it out**, enter a JSON payload, and click **Execute**.
   - With authorization: returns `201 Created`.
   - To test 401: click **Authorize** again, click **Logout**, and execute `POST /users`—you will receive the standard `401 UNAUTHORIZED` error.

---

### Method 2: Command Line Testing with `curl`

Below are copy-paste commands to test each scenario using `curl`:

#### Scenario A: Missing API Key (Fails with 401 Unauthorized)
```bash
curl -i -X POST http://127.0.0.1:8000/users \
  -H "Content-Type: application/json" \
  -d "{\"name\": \"Alice\", \"email\": \"alice@example.com\"}"
```
*Expected Output:* Status `401 Unauthorized` with `code: "UNAUTHORIZED"`.

#### Scenario B: Invalid API Key (Fails with 401 Unauthorized)
```bash
curl -i -X POST http://127.0.0.1:8000/users \
  -H "Content-Type: application/json" \
  -H "X-API-Key: invalid-key" \
  -d "{\"name\": \"Alice\", \"email\": \"alice@example.com\"}"
```
*Expected Output:* Status `401 Unauthorized` with `message: "Invalid API key provided. Access denied."`.

#### Scenario C: Valid API Key & Valid Payload (Succeeds with 201 Created)
```bash
curl -i -X POST http://127.0.0.1:8000/users \
  -H "Content-Type: application/json" \
  -H "X-API-Key: swynex-secret-api-key-2026" \
  -d "{\"name\": \"Alice Cooper\", \"email\": \"alice.cooper@example.com\"}"
```
*Expected Output:* Status `201 Created` with JSON:
```json
{
  "id": 6,
  "name": "Alice Cooper",
  "email": "alice.cooper@example.com"
}
```

#### Scenario D: Invalid Payload Validation (Fails with 422 Unprocessable Content)
Send an empty body, blank name, or invalid email address with the valid API key:
```bash
curl -i -X POST http://127.0.0.1:8000/users \
  -H "Content-Type: application/json" \
  -H "X-API-Key: swynex-secret-api-key-2026" \
  -d "{\"name\": \"  \", \"email\": \"invalid-email-format\"}"
```
*Expected Output:* Status `422` with `code: "VALIDATION_ERROR"` and detailed error diagnostics.

#### Scenario E: Duplicate Email Conflict (Fails with 409 Conflict)
Attempt to create another user with an already registered email:
```bash
curl -i -X POST http://127.0.0.1:8000/users \
  -H "Content-Type: application/json" \
  -H "X-API-Key: swynex-secret-api-key-2026" \
  -d "{\"name\": \"Alice Duplicate\", \"email\": \"alice.cooper@example.com\"}"
```
*Expected Output:* Status `409 Conflict` with `code: "CONFLICT"`.

#### Scenario F: Update User with Valid API Key (Succeeds with 200 OK)
```bash
curl -i -X PUT http://127.0.0.1:8000/users/6 \
  -H "Content-Type: application/json" \
  -H "X-API-Key: swynex-secret-api-key-2026" \
  -d "{\"name\": \"Alice Cooper Updated\"}"
```
*Expected Output:* Status `200 OK` with updated user record.

#### Scenario G: Delete User with Valid API Key (Succeeds with 200 OK)
```bash
curl -i -X DELETE http://127.0.0.1:8000/users/6 \
  -H "X-API-Key: swynex-secret-api-key-2026"
```
*Expected Output:* Status `200 OK` with:
```json
{
  "message": "User deleted successfully"
}
```

#### Scenario H: Non-Existent User Lookup (Fails with 404 Not Found)
```bash
curl -i -X GET http://127.0.0.1:8000/users/999999
```
*Expected Output:* Status `404 Not Found` with `code: "NOT_FOUND"`.

---

### Method 3: PowerShell Testing with `Invoke-RestMethod`

If using Windows PowerShell:

```powershell
# Set API Key variable
$apiKey = "swynex-secret-api-key-2026"
$headers = @{
    "Content-Type" = "application/json"
    "X-API-Key"    = $apiKey
}

# 1. Create a User (Protected)
$newUser = @{
    name  = "Bruce Wayne"
    email = "bruce.wayne@example.com"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri "http://127.0.0.1:8000/users" -Method Post -Headers $headers -Body $newUser
$response

# 2. Retrieve the Created User (Public)
$userId = $response.id
Invoke-RestMethod -Uri "http://127.0.0.1:8000/users/$userId" -Method Get

# 3. Test Unauthorized Access (Should throw 401)
try {
    Invoke-RestMethod -Uri "http://127.0.0.1:8000/users" -Method Post -Body $newUser -ContentType "application/json"
} catch {
    $_.Exception.Response.StatusCode
    $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
    $reader.ReadToEnd()
}

# 4. Delete the User (Protected)
Invoke-RestMethod -Uri "http://127.0.0.1:8000/users/$userId" -Method Delete -Headers $headers
```

---

### Method 4: Automated Test Suite with `pytest`

The repository includes a complete automated test suite in `tests/test_api.py`. The suite uses an in-memory SQLite database to run isolated tests without mutating production or local PostgreSQL data.

Run the entire test suite from the repository root:

```bash
pytest -v
```

**Test Coverage Summary:**

```text
tests/test_api.py::test_health_check_public_access                    PASSED
tests/test_api.py::test_create_user_unauthorized_when_missing_api_key  PASSED
tests/test_api.py::test_create_user_unauthorized_when_invalid_api_key  PASSED
tests/test_api.py::test_update_user_unauthorized_when_missing_api_key  PASSED
tests/test_api.py::test_delete_user_unauthorized_when_missing_api_key  PASSED
tests/test_api.py::test_bearer_token_authentication_supported          PASSED
tests/test_api.py::test_payload_validation_empty_body                  PASSED
tests/test_api.py::test_payload_validation_invalid_email               PASSED
tests/test_api.py::test_payload_validation_blank_whitespace_name       PASSED
tests/test_api.py::test_payload_validation_name_too_short              PASSED
tests/test_api.py::test_path_parameter_validation_invalid_id           PASSED
tests/test_api.py::test_full_user_crud_flow_with_auth                  PASSED
tests/test_api.py::test_duplicate_email_conflict_error                 PASSED
tests/test_api.py::test_user_not_found_consistent_error                PASSED
```

---

## Interactive API Documentation

Once the server is running, explore the auto-generated interactive documentation:

- **Swagger UI:** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) (Includes "Authorize" button to set `X-API-Key`)
- **ReDoc:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
