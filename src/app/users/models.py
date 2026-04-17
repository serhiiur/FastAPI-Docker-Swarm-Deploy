from app.core.models import Base

from .schemas import CreateUser


class User(Base, CreateUser, table=True):
  """Database model to represent a user in the database."""
