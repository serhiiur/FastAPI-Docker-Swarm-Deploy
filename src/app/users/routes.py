from fastcrud import crud_router

from app.core.dependencies import get_db_session

from .models import User
from .schemas import CreateUser, UpdateUser

router = crud_router(
    session=get_db_session,
    model=User,
    create_schema=CreateUser,
    update_schema=UpdateUser,
    path="/api/users",
    tags=["users"],
)
