SWYNEX Intern Project

A simple backend service built with Python and FastAPI.
The project currently includes a health-check endpoint to verify that the API service is running.

Project Structure

SWYNEX_Intern_Project/
│
├── .venv/                  # Local virtual environment (not committed)
│
└── fastapi_project/
    ├── app/
    │   ├── main.py         # FastAPI application and health-check endpoint
    │   └── .env            # Local environment configuration (not committed)
    │
    ├── .gitignore
    ├── README.md
    └── requirements.txt

The Git repository is initialized at the SWYNEX_Intern_Project root.

Requirements

Python 3.10+ recommended

pip

Git

Setup

1. Clone the repository

git clone <YOUR_GITHUB_REPOSITORY_URL>
cd SWYNEX_Intern_Project

2. Create a virtual environment

Windows PowerShell:

python -m venv .venv

3. Activate the virtual environment

Windows PowerShell:

.venv\Scripts\Activate.ps1

If activation is successful, your terminal should show (.venv).

4. Install dependencies

pip install -r fastapi_project/requirements.txt

Environment Configuration

Environment-specific values should be stored in a .env file and should not be committed to Git.

For example:

fastapi_project/
└── app/
    └── .env

If the project requires environment variables, create the .env file locally and add the required variables.

Never commit API keys, passwords, tokens, or other secrets to GitHub.

Run the Application

From the repository root:

uvicorn fastapi_project.app.main:app --reload

The API will normally be available at:

http://127.0.0.1:8000

Health Check

The application provides the following endpoint:

GET /health-check

Open:

http://127.0.0.1:8000/health-check

Example response:

{
  "status": "ok",
  "service": "FastAPI",
  "message": "Service is running smoothly"
}

API Documentation

FastAPI automatically provides interactive API documentation.

Swagger UI:

http://127.0.0.1:8000/docs

ReDoc:

http://127.0.0.1:8000/redoc

Development

Start the server with:

uvicorn fastapi_project.app.main:app --reload

The --reload option automatically restarts the development server when code changes are detected.

Git Notes

The local virtual environment should not be committed to GitHub. The repository contains requirements.txt so that dependencies can be recreated on another machine.

Typical workflow:

git add .
git commit -m "Update backend service"
git push

User Management API

The backend has been extended with user CRUD operations using FastAPI and SQLAlchemy.

Project Features

- Health check endpoint
- Create a new user
- Retrieve a user by ID
- Update an existing user
- Delete a user
- Input validation with Pydantic
- SQLAlchemy ORM models and database session management

API Endpoints

Create User

Method: POST
Endpoint: /users

Request body:

{
  "name": "John Doe",
  "email": "john@example.com"
}

Example response:

{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com"
}

Get User by ID

Method: GET
Endpoint: /users/{user_id}

Example response:

{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com"
}

Update User

Method: PUT
Endpoint: /users/{user_id}

Request body:

{
  "name": "John Updated",
  "email": "johnupdated@example.com"
}

Example response:

{
  "id": 1,
  "name": "John Updated",
  "email": "johnupdated@example.com"
}

Delete User

Method: DELETE
Endpoint: /users/{user_id}

Example response:

{
  "message": "User deleted successfully"
}

Validation Models

The API uses Pydantic models to validate request and response payloads.

UserRequest model:

- name: string
- email: valid email address

UserResponse model:

- id: integer
- name: string
- email: valid email address

These models ensure incoming user data is properly structured before being processed by the application.

Database Models

The project includes a SQLAlchemy ORM model for the users table.

User table fields:

- id: primary key
- name: required string
- email: required unique string

This table is created automatically when the application starts using the SQLAlchemy metadata.

Database Session Configuration

The application includes a database connection setup and session management using SQLAlchemy:

- Database URL is loaded from environment variables
- Engine is created using create_engine()
- SessionLocal is configured with sessionmaker()
- get_db() provides a database session for each request
- Base.metadata.create_all() ensures the tables exist

Example environment variable:

DATABASE_URL=sqlite:///./users.db

This configuration allows the API to interact with the database and manage user records efficiently.

Database Files and Modules

The project now includes the following database-related files:

- app/db.py: database connection and session setup
- app/tables.py: database models and ORM table definitions
- app/validators.py: request/response validation models
- app/main.py: API routes and CRUD logic

This structure keeps the API, validation layer, and database layer organized and easy to maintain.


