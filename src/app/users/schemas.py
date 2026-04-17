from pydantic import EmailStr, PositiveInt
from sqlmodel import Field, SQLModel


class CreateUser(SQLModel):
  """Request schema to create a user."""

  name: str = Field(
    description="Name of the user",
  )
  email: EmailStr = Field(
    description="Email of the user",
    unique=True,
    index=True,
  )
  age: PositiveInt = Field(
    description="Age of the user",
  )
  is_employed: bool = Field(
    default=True,
    description="Whether the user is employed or not",
  )


class UpdateUser(SQLModel):
  """Request schema to update a user."""

  name: str | None = Field(
    default=None,
    description="Optional new name of the user",
  )
  email: EmailStr | None = Field(
    default=None,
    description="Optional new email of the user",
  )
  age: PositiveInt | None = Field(
    default=None,
    description="Optional new age of the user",
  )
  is_employed: bool | None = Field(
    default=None,
    description="Optional new employment status",
  )
