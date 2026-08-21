from fastapi import APIRouter, status

from app.api.deps import SessionDep
from app.models.user import User, UserCreate, UserRead
from app.services import user_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def signup(user_in: UserCreate, session: SessionDep) -> User:
    """Register a new GamerZone account.

    The router stays thin on purpose: it only deals with HTTP concerns (the request
    body, the status code, the response shape) and delegates the actual rules to the
    service layer. response_model=UserRead is the security boundary - even though this
    returns a full User object, FastAPI serialises it through UserRead, so
    hashed_password physically cannot appear in the response.
    """
    return await user_service.create_user(session, user_in)
