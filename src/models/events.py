from pydantic import BaseModel
from database.base import Base
from sqlalchemy import ARRAY, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime


class EventRequest(BaseModel):
    title: str
    date: datetime
    description: str
    tags: list[str]
    location: str

    class Config:
        schema_extra = {
            "example": {
                "title": "Event title",
                "date": "2024-08-28T14:38:04",
                "description": "Event description",
                "tags": ["tag1", "tag2"],
                "location": "online",
            }
        }


class EventCreate(EventRequest):
    pass


class EventUpdate(EventCreate):
    title: str | None = None
    date: datetime | None = None
    description: str | None = None
    tags: list[str] | None = None
    location: str | None = None


class Event(Base):
    __tablename__ = "events"

    id: Mapped[int] = mapped_column(primary_key=True)
    creator: Mapped[str] = mapped_column(String(32))
    title: Mapped[str] = mapped_column(String(64))
    date: Mapped[datetime] = mapped_column(DateTime)
    description: Mapped[str] = mapped_column(String(256))
    tags: Mapped[list[str]] = mapped_column(ARRAY(String(16)))
    location: Mapped[str] = mapped_column(String(64))
