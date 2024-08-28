from pydantic import BaseModel, EmailStr
from database.base import Base
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column


class SignInUser(BaseModel):
    email: EmailStr
    password: str

    class Config:
        schema_extra = {
            "example": {
                "email": "name@server.com",
                "password": "secret",
            }
        }


class SignUpUser(SignInUser):
    pass


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(32), unique=True)
    password: Mapped[str] = mapped_column(String(72))
