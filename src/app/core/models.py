from datetime import datetime

from sqlalchemy import func
from sqlmodel import Field, SQLModel


class Base(SQLModel):
  """Base declarative SQL model."""

  id: int | None = Field(default=None, primary_key=True)
  created_at: datetime = Field(default_factory=func.now)
  updated_at: datetime = Field(
    default_factory=func.now,
    sa_column_kwargs={"onupdate": func.now},
  )
