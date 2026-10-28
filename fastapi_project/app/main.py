import logging
from typing import List
from fastapi import Depends, FastAPI, HTTPException, Path, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette.exceptions import HTTPException as StarletteHTTPException

try:
    from .auth import verify_api_key
    from .db import get_db
    from .tables import User
    from .validators import (
        ErrorResponse,
        MessageResponse,
        UserRequest,
        UserResponse,
        UserUpdateRequest,
    )
except ImportError:
    try:
        from app.auth import verify_api_key
        from app.db import get_db
        from app.tables import User
        from app.validators import (
            ErrorResponse,
            MessageResponse,
            UserRequest,
            UserResponse,
            UserUpdateRequest,
        )
    except ImportError:
        from auth import verify_api_key
        from db import get_db
        from tables import User
        from validators import (
            ErrorResponse,
            MessageResponse,
            UserRequest,
            UserResponse,
            UserUpdateRequest,
        )

# Configure logger
logger = logging.getLogger("swynex_api")
logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="SWYNEX User Management API",
    description=(
        "FastAPI service with API key authentication, strict payload validation, "
        "and standardized, consistent error responses."
    ),
    version="1.0.0",
)

# Standard HTTP status code mapping to machine-readable string codes
STATUS_CODE_MAP = {
    400: "BAD_REQUEST",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
    409: "CONFLICT",
    422: "VALIDATION_ERROR",
    500: "INTERNAL_SERVER_ERROR",
}


# ==========================================
# Exception Handlers for Consistent Errors
# ==========================================

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    code = STATUS_CODE_MAP.get(exc.status_code, "HTTP_ERROR")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "status": "error",
            "code": code,
            "message": exc.detail if isinstance(exc.detail, str) else str(exc.detail),
            "details": None,
        },
        headers=getattr(exc, "headers", None),
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    details = []
    for error in exc.errors():
        loc = [str(x) for x in error.get("loc", []) if x not in ("body",)]
        field_name = ".".join(loc) if loc else "payload"
        msg = error.get("msg", "Invalid value")
        if msg.startswith("Value error, "):
            msg = msg[len("Value error, "):]
        details.append({"field": field_name, "message": msg})

    return JSONResponse(
        status_code=getattr(status, "HTTP_422_UNPROCESSABLE_CONTENT", status.HTTP_422_UNPROCESSABLE_ENTITY),
        content={
            "status": "error",
            "code": "VALIDATION_ERROR",
            "message": "Input validation failed. Please review the provided fields.",
            "details": details,
        },
    )


@app.exception_handler(IntegrityError)
async def sqlalchemy_integrity_error_handler(request: Request, exc: IntegrityError):
    logger.warning(f"Database IntegrityError caught: {exc.orig}")
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "status": "error",
            "code": "CONFLICT",
            "message": "Database constraint violation. A user with this unique attribute (such as email) already exists.",
            "details": None,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled server exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "status": "error",
            "code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected internal server error occurred. Please try again later.",
            "details": None,
        },
    )


# ==========================================
# Common response documentation for OpenAPI
# ==========================================
COMMON_ERROR_RESPONSES = {
    400: {"model": ErrorResponse, "description": "Bad Request"},
    401: {"model": ErrorResponse, "description": "Unauthorized - Missing or Invalid API Key"},
    404: {"model": ErrorResponse, "description": "Resource Not Found"},
    409: {"model": ErrorResponse, "description": "Conflict - Duplicate unique value"},
    422: {"model": ErrorResponse, "description": "Validation Error - Invalid payload or parameters"},
    500: {"model": ErrorResponse, "description": "Internal Server Error"},
}


# ==========================================
# Routes
# ==========================================

@app.get(
    "/health-check",
    tags=["System"],
    summary="Health check",
    description="Public endpoint to verify the service status."
)
def health_check():
    return {
        "status": "ok",
        "service": "FastAPI",
        "message": "Service is running smoothly",
    }


@app.get(
    "/users",
    response_model=List[UserResponse],
    tags=["Users"],
    summary="List all users",
    description="Retrieve a list of all registered users."
)
def list_users(db: Session = Depends(get_db)):
    users = db.scalars(select(User).order_by(User.id)).all()
    return users


@app.get(
    "/users/{user_id}",
    response_model=UserResponse,
    responses=COMMON_ERROR_RESPONSES,
    tags=["Users"],
    summary="Get user details by ID",
    description="Retrieve details for a specific user by their ID."
)
def get_user_details(
    user_id: int = Path(..., gt=0, description="The positive integer ID of the user"),
    db: Session = Depends(get_db),
):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )
    return user


@app.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    responses=COMMON_ERROR_RESPONSES,
    tags=["Users (Protected)"],
    summary="Create a new user (Protected)",
    description="Protected endpoint requiring 'X-API-Key' authentication header to create a new user record."
)
def create_user(
    user: UserRequest,
    db: Session = Depends(get_db),
    _api_key: str = Depends(verify_api_key),
):
    # Check for existing email conflict before insert
    existing_user = db.scalars(select(User).where(User.email == user.email)).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A user with email '{user.email}' already exists.",
        )

    new_user = User(name=user.name, email=user.email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@app.put(
    "/users/{user_id}",
    response_model=UserResponse,
    responses=COMMON_ERROR_RESPONSES,
    tags=["Users (Protected)"],
    summary="Update an existing user (Protected)",
    description="Protected endpoint requiring 'X-API-Key' authentication header to update an existing user record."
)
def update_user(
    updated_user: UserUpdateRequest,
    user_id: int = Path(..., gt=0, description="The positive integer ID of the user"),
    db: Session = Depends(get_db),
    _api_key: str = Depends(verify_api_key),
):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )

    # If updating email, ensure no conflict with another user
    if updated_user.email is not None and updated_user.email != user.email:
        existing_email = db.scalars(
            select(User).where(User.email == updated_user.email, User.id != user_id)
        ).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"A user with email '{updated_user.email}' already exists.",
            )
        user.email = updated_user.email

    if updated_user.name is not None:
        user.name = updated_user.name

    db.commit()
    db.refresh(user)
    return user


@app.delete(
    "/users/{user_id}",
    response_model=MessageResponse,
    responses=COMMON_ERROR_RESPONSES,
    tags=["Users (Protected)"],
    summary="Delete a user (Protected)",
    description="Protected endpoint requiring 'X-API-Key' authentication header to delete a user record."
)
def delete_user(
    user_id: int = Path(..., gt=0, description="The positive integer ID of the user"),
    db: Session = Depends(get_db),
    _api_key: str = Depends(verify_api_key),
):
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {user_id} not found",
        )

    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}