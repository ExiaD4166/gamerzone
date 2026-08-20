from datetime import datetime, timezone

from sqlalchemy import Column, DateTime
from sqlmodel import Field, SQLModel


class DownloadItemBase(SQLModel):
    """Fields shared by every variant below - not a table itself (no table=True)."""

    title: str
    category: str
    url: str
    description: str | None = None


class DownloadItem(DownloadItemBase, table=True):
    """The actual database table. Adds fields that only exist once a row is stored:
    an id assigned by Postgres, and a server-set creation timestamp."""

    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )


class DownloadItemCreate(DownloadItemBase):
    """What a client sends to create one - deliberately can't include id/created_at,
    since the server decides those, not the caller."""


class DownloadItemRead(DownloadItemBase):
    """What the API returns - the base fields plus the server-assigned ones."""

    id: int
    created_at: datetime


class DownloadItemUpdate(SQLModel):
    """A partial-update schema: every field optional, since PATCH only sends what's changing."""

    title: str | None = None
    category: str | None = None
    url: str | None = None
    description: str | None = None
