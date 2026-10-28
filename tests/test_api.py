import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from fastapi_project.app.main import app
from fastapi_project.app.db import get_db
from fastapi_project.app.tables import Base
from fastapi_project.app.auth import EXPECTED_API_KEY

# In-memory SQLite database dedicated for tests
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
    expire_on_commit=False,
)


@pytest.fixture(autouse=True)
def setup_test_db():
    """Create fresh tables for every test run and clean up afterwards."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)
VALID_API_KEY = EXPECTED_API_KEY
AUTH_HEADERS = {"X-API-Key": VALID_API_KEY}


# ============================================================================
# 1. Health Check (Public Endpoint)
# ============================================================================

def test_health_check_public_access():
    """Verify health check is publicly accessible without authentication."""
    response = client.get("/health-check")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "FastAPI"


# ============================================================================
# 2. Authentication Protection & Consistent Error Responses
# ============================================================================

def test_create_user_unauthorized_when_missing_api_key():
    """POST /users without API key header should return 401 UNAUTHORIZED."""
    payload = {"name": "Alice Tester", "email": "alice@example.com"}
    response = client.post("/users", json=payload)
    assert response.status_code == 401

    data = response.json()
    assert data["status"] == "error"
    assert data["code"] == "UNAUTHORIZED"
    assert "Authentication required" in data["message"]


def test_create_user_unauthorized_when_invalid_api_key():
    """POST /users with an invalid API key should return 401 UNAUTHORIZED."""
    payload = {"name": "Alice Tester", "email": "alice@example.com"}
    response = client.post("/users", json=payload, headers={"X-API-Key": "wrong-key"})
    assert response.status_code == 401

    data = response.json()
    assert data["status"] == "error"
    assert data["code"] == "UNAUTHORIZED"
    assert "Invalid API key" in data["message"]


def test_update_user_unauthorized_when_missing_api_key():
    """PUT /users/{id} without API key should return 401 UNAUTHORIZED."""
    response = client.put("/users/1", json={"name": "New Name"})
    assert response.status_code == 401
    assert response.json()["code"] == "UNAUTHORIZED"


def test_delete_user_unauthorized_when_missing_api_key():
    """DELETE /users/{id} without API key should return 401 UNAUTHORIZED."""
    response = client.delete("/users/1")
    assert response.status_code == 401
    assert response.json()["code"] == "UNAUTHORIZED"


def test_bearer_token_authentication_supported():
    """Protected endpoints should also accept 'Authorization: Bearer <API_KEY>'."""
    payload = {"name": "Bearer User", "email": "bearer@example.com"}
    bearer_headers = {"Authorization": f"Bearer {VALID_API_KEY}"}
    response = client.post("/users", json=payload, headers=bearer_headers)
    assert response.status_code == 201
    assert response.json()["name"] == "Bearer User"


# ============================================================================
# 3. Payload Validation & Consistent 422 Error Responses
# ============================================================================

def test_payload_validation_empty_body():
    """Empty request payload returns 422 with VALIDATION_ERROR code and field details."""
    response = client.post("/users", json={}, headers=AUTH_HEADERS)
    assert response.status_code == 422

    data = response.json()
    assert data["status"] == "error"
    assert data["code"] == "VALIDATION_ERROR"
    assert "Input validation failed" in data["message"]
    fields = [d["field"] for d in data["details"]]
    assert "name" in fields
    assert "email" in fields


def test_payload_validation_invalid_email():
    """Invalid email format returns 422 with clear field-level error detail."""
    payload = {"name": "Charlie", "email": "not-a-valid-email"}
    response = client.post("/users", json=payload, headers=AUTH_HEADERS)
    assert response.status_code == 422

    data = response.json()
    assert data["code"] == "VALIDATION_ERROR"
    email_errors = [d for d in data["details"] if d["field"] == "email"]
    assert len(email_errors) > 0


def test_payload_validation_blank_whitespace_name():
    """Whitespace-only name returns 422 validation error."""
    payload = {"name": "    ", "email": "charlie@example.com"}
    response = client.post("/users", json=payload, headers=AUTH_HEADERS)
    assert response.status_code == 422

    data = response.json()
    assert data["code"] == "VALIDATION_ERROR"
    name_errors = [d for d in data["details"] if d["field"] == "name"]
    assert len(name_errors) > 0


def test_payload_validation_name_too_short():
    """Name shorter than 2 characters returns 422 validation error."""
    payload = {"name": "X", "email": "charlie@example.com"}
    response = client.post("/users", json=payload, headers=AUTH_HEADERS)
    assert response.status_code == 422

    data = response.json()
    assert data["code"] == "VALIDATION_ERROR"


def test_path_parameter_validation_invalid_id():
    """Negative or zero user_id in path parameter returns 422 VALIDATION_ERROR."""
    response = client.get("/users/0")
    assert response.status_code == 422
    assert response.json()["code"] == "VALIDATION_ERROR"


# ============================================================================
# 4. Successful CRUD & Business Logic Error Responses
# ============================================================================

def test_full_user_crud_flow_with_auth():
    """Complete lifecycle: create user, get user, update user, delete user."""
    # 1. Create User
    create_payload = {"name": "Diana Prince", "email": "diana@example.com"}
    create_res = client.post("/users", json=create_payload, headers=AUTH_HEADERS)
    assert create_res.status_code == 201
    created_user = create_res.json()
    user_id = created_user["id"]
    assert created_user["name"] == "Diana Prince"
    assert created_user["email"] == "diana@example.com"

    # 2. Get User (Public Read)
    get_res = client.get(f"/users/{user_id}")
    assert get_res.status_code == 200
    assert get_res.json()["name"] == "Diana Prince"

    # 3. Update User (Protected)
    update_payload = {"name": "Diana Wayne"}
    update_res = client.put(f"/users/{user_id}", json=update_payload, headers=AUTH_HEADERS)
    assert update_res.status_code == 200
    assert update_res.json()["name"] == "Diana Wayne"
    assert update_res.json()["email"] == "diana@example.com"

    # 4. Delete User (Protected)
    del_res = client.delete(f"/users/{user_id}", headers=AUTH_HEADERS)
    assert del_res.status_code == 200
    assert del_res.json()["message"] == "User deleted successfully"

    # 5. Verify 404 NOT_FOUND after deletion
    verify_res = client.get(f"/users/{user_id}")
    assert verify_res.status_code == 404
    assert verify_res.json()["code"] == "NOT_FOUND"


def test_duplicate_email_conflict_error():
    """Creating user with duplicate email returns consistent 409 CONFLICT error."""
    payload = {"name": "User One", "email": "duplicate@example.com"}
    res1 = client.post("/users", json=payload, headers=AUTH_HEADERS)
    assert res1.status_code == 201

    # Attempt to create another user with identical email
    res2 = client.post("/users", json=payload, headers=AUTH_HEADERS)
    assert res2.status_code == 409

    data = res2.json()
    assert data["status"] == "error"
    assert data["code"] == "CONFLICT"
    assert "already exists" in data["message"]


def test_user_not_found_consistent_error():
    """Non-existent user ID returns consistent 404 NOT_FOUND error."""
    response = client.get("/users/999999")
    assert response.status_code == 404

    data = response.json()
    assert data["status"] == "error"
    assert data["code"] == "NOT_FOUND"
    assert "User with ID 999999 not found" in data["message"]
