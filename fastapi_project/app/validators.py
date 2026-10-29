import re
from typing import Dict, List, Optional
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


class UserRequest(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Full name of the user (2-100 characters)",
        examples=["John Doe"]
    )
    email: EmailStr = Field(
        ...,
        max_length=255,
        description="Valid email address of the user",
        examples=["john.doe@example.com"]
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "John Doe",
                "email": "john.doe@example.com"
            }
        }
    }

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        trimmed = value.strip()
        if len(trimmed) < 2:
            raise ValueError("Name must be at least 2 non-whitespace characters long.")
        if not re.search(r"[a-zA-Z]", trimmed):
            raise ValueError("Name must contain at least one alphabetic character.")
        return trimmed

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class UserUpdateRequest(BaseModel):
    name: Optional[str] = Field(
        default=None,
        min_length=2,
        max_length=100,
        description="Updated full name of the user (optional)",
        examples=["Jane Doe"]
    )
    email: Optional[EmailStr] = Field(
        default=None,
        max_length=255,
        description="Updated email address of the user (optional)",
        examples=["jane.doe@example.com"]
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Jane Doe",
                "email": "jane.doe@example.com"
            }
        }
    }

    @field_validator("name")
    @classmethod
    def validate_update_name(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        trimmed = value.strip()
        if len(trimmed) < 2:
            raise ValueError("Name must be at least 2 non-whitespace characters long.")
        if not re.search(r"[a-zA-Z]", trimmed):
            raise ValueError("Name must contain at least one alphabetic character.")
        return trimmed

    @field_validator("email")
    @classmethod
    def normalize_update_email(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        return value.strip().lower()

    @model_validator(mode="after")
    def validate_at_least_one_field(self) -> "UserUpdateRequest":
        if self.name is None and self.email is None:
            raise ValueError("At least one field ('name' or 'email') must be provided for update.")
        return self


class UserResponse(BaseModel):
    id: int = Field(..., description="Unique user identifier", examples=[1])
    name: str = Field(..., description="Full name of the user", examples=["John Doe"])
    email: EmailStr = Field(..., description="Valid email address", examples=["john.doe@example.com"])

    model_config = {"from_attributes": True}


class MessageResponse(BaseModel):
    message: str = Field(..., description="Success message", examples=["User deleted successfully"])


class DocumentationLinks(BaseModel):
    swagger_ui: str = Field(..., description="Swagger UI URL", examples=["/docs"])
    redoc: str = Field(..., description="ReDoc URL", examples=["/redoc"])
    openapi_json: str = Field(..., description="OpenAPI JSON Schema URL", examples=["/openapi.json"])


class RootResponse(BaseModel):
    name: str = Field(..., description="API Name", examples=["SWYNEX User Management API"])
    version: str = Field(..., description="API Version", examples=["1.0.0"])
    status: str = Field(..., description="Operational status", examples=["online"])
    documentation: DocumentationLinks
    endpoints: Dict[str, str] = Field(..., description="List of primary endpoints")


class SeedResponse(BaseModel):
    status: str = Field(default="ok", description="Operation status indicator", examples=["ok"])
    message: str = Field(..., description="Operation summary", examples=["Sample data seeding complete. Created 6 new user(s)."])
    users_created: int = Field(..., description="Number of newly inserted users", examples=[6])
    total_users: int = Field(..., description="Total count of users currently in the database", examples=[6])


class ErrorDetail(BaseModel):
    field: Optional[str] = Field(default=None, description="Payload/parameter field that caused error", examples=["email"])
    message: str = Field(..., description="Specific error description", examples=["value is not a valid email address"])


class ErrorResponse(BaseModel):
    status: str = Field(default="error", description="Error status indicator", examples=["error"])
    code: str = Field(..., description="Machine-readable error classification", examples=["VALIDATION_ERROR", "UNAUTHORIZED", "NOT_FOUND", "CONFLICT"])
    message: str = Field(..., description="Human-readable summary of the error", examples=["Input validation failed"])
    details: Optional[List[ErrorDetail]] = Field(default=None, description="Detailed list of validation issues or extra context")
