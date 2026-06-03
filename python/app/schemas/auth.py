from pydantic import BaseModel, Field, field_validator


class LoginRequest(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=20
    )

    pwd: str = Field(
        min_length=6,
        max_length=50
    )

    @field_validator("pwd")
    @classmethod
    def validate_password(cls, value):
        if not any(char.isdigit() for char in value):
            raise ValueError("Password must contain at least one digit")
        if not any(char.isalpha() for char in value):
            raise ValueError("Password must contain at least one letter")
        return value