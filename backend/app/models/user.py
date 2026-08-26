from datetime import datetime, timezone

from pydantic import EmailStr
from sqlalchemy import Column, DateTime
from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    # The UNIQUE constraint, not the check in the service layer, is what actually
    # holds under concurrency.
    email: EmailStr = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True, min_length=3, max_length=32)


class User(UserBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
    # Granted out of band. Absent from UserCreate so signup can never set it.
    is_superuser: bool = Field(default=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    # Tokens issued before this moment are refused, which is how a password reset
    # signs the account out everywhere at once. Null means it has never changed.
    password_changed_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )


class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class PasswordResetRequest(SQLModel):
    email: EmailStr


class PasswordResetConfirm(SQLModel):
    token: str
    # Same minimum as signup, so a reset can't be used to set a weaker password
    # than registration would have accepted.
    new_password: str = Field(min_length=8, max_length=128)


class UserRead(UserBase):
    """What the API sends back: no password or hash, so neither can leak."""

    id: int
    is_verified: bool
    is_superuser: bool
    created_at: datetime
