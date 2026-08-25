from datetime import datetime, timezone

from pydantic import EmailStr
from sqlalchemy import Column, DateTime
from sqlmodel import Field, SQLModel


class UserBase(SQLModel):
    """Identity fields shared by the table and the public schemas.

    unique=True creates a UNIQUE constraint in Postgres - the database itself
    refuses a duplicate, which is the only guarantee that holds under concurrency.
    index=True makes lookups by email/username fast, which matters because every
    single login will query by email.
    """

    email: EmailStr = Field(unique=True, index=True)
    username: str = Field(unique=True, index=True, min_length=3, max_length=32)


class User(UserBase, table=True):
    """The users table. Note there is no `password` column anywhere - only a hash."""

    id: int | None = Field(default=None, primary_key=True)
    hashed_password: str
    is_active: bool = Field(default=True)
    is_verified: bool = Field(default=False)
    # Admin flag. Signup can never set this - it is granted deliberately, out of band,
    # which is why it lives on the table but not on UserCreate.
    is_superuser: bool = Field(default=False)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    # Set whenever the password changes. Access tokens issued before this moment are
    # refused, which is how a reset signs the account out everywhere at once.
    # Nullable: accounts that have never changed their password simply have no cutoff.
    password_changed_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )


class UserCreate(UserBase):
    """What a client sends to sign up. This is the only place a plain password
    exists, and it never reaches the database in this form."""

    password: str = Field(min_length=8, max_length=128)


class PasswordResetRequest(SQLModel):
    """Body of "I forgot my password" - just the address to send the link to."""

    email: EmailStr


class PasswordResetConfirm(SQLModel):
    """Body of the actual reset: the token from the emailed link, and the new password.

    Reuses the same min_length as signup so the rules can't be sidestepped by
    resetting into a weaker password than registration would have allowed.
    """

    token: str
    new_password: str = Field(min_length=8, max_length=128)


class UserRead(UserBase):
    """What the API sends back. Deliberately has no password or hashed_password
    field, so neither can ever leak through a response."""

    id: int
    is_verified: bool
    # Safe to expose: it's the caller's own role, and the frontend needs it to decide
    # whether to show admin controls. The server still enforces it independently.
    is_superuser: bool
    created_at: datetime
