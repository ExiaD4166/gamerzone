from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import CurrentUserDep, SessionDep
from app.core.security import create_access_token
from app.models.token import Token
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


@router.post("/login", response_model=Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: SessionDep,
) -> Token:
    """Exchange credentials for an access token.

    Takes form data rather than JSON, with the credential in a field called
    `username`, because the OAuth2 password flow specifies exactly that. We treat that
    field as the user's email. Following the spec is what makes /docs' Authorize
    button and any standard OAuth2 client work against this API.
    """
    user = await user_service.authenticate_user(session, form_data.username, form_data.password)
    if user is None:
        # One identical message whether the email is unknown or the password is wrong.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return Token(access_token=create_access_token(user.id))


@router.get("/me", response_model=UserRead)
async def read_current_user(current_user: CurrentUserDep) -> User:
    """Return the signed-in user's own profile.

    The body is a single line because CurrentUserDep already did the work: extracted
    the token, verified its signature and expiry, loaded the user, and checked the
    account is active. This is the pattern every protected endpoint will follow.
    """
    return current_user
