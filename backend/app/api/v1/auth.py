from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import EmailStr

from app.api.deps import CurrentUserDep, SessionDep, oauth2_scheme
from app.core.security import create_access_token, decode_access_token
from app.core.tokens import verify_email_verification_token
from app.db.redis import blacklist_token
from app.models.token import Token
from app.models.user import (
    PasswordResetConfirm,
    PasswordResetRequest,
    User,
    UserCreate,
    UserRead,
)
from app.services import user_service
from app.services.mail_service import send_password_reset_email, send_verification_email

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def signup(
    user_in: UserCreate, session: SessionDep, background_tasks: BackgroundTasks
) -> User:
    """Register a new GamerZone account and send its verification email.

    The router stays thin on purpose: it only deals with HTTP concerns (the request
    body, the status code, the response shape) and delegates the actual rules to the
    service layer. response_model=UserRead is the security boundary - even though this
    returns a full User object, FastAPI serialises it through UserRead, so
    hashed_password physically cannot appear in the response.

    The email is queued as a background task rather than awaited, so talking to the
    SMTP server doesn't hold up the response. FastAPI runs it after the 201 is sent.
    """
    user = await user_service.create_user(session, user_in)
    background_tasks.add_task(send_verification_email, user.email, user.username)
    return user


@router.get("/verify")
async def verify_email(token: str, session: SessionDep) -> dict[str, str]:
    """Confirm an email address from the link in the verification message.

    A GET because this is reached by clicking a link. The token itself carries the
    address and its own issue time, so nothing about it had to be stored server-side.
    """
    email = verify_email_verification_token(token)
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This verification link is invalid or has expired.",
        )

    user = await user_service.get_user_by_email(session, email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This verification link is invalid or has expired.",
        )

    await user_service.mark_email_verified(session, user)
    return {"message": "Email verified successfully. You can now sign in and browse downloads."}


@router.post("/resend-verification", status_code=status.HTTP_202_ACCEPTED)
async def resend_verification(
    email: EmailStr, session: SessionDep, background_tasks: BackgroundTasks
) -> dict[str, str]:
    """Send a fresh verification link.

    Always reports the same thing, whether or not that address has an account and
    whether or not it is already verified. Saying "no such user" here would let an
    attacker discover which addresses are registered - the same user-enumeration
    problem the login endpoint avoids.
    """
    user = await user_service.get_user_by_email(session, email)
    if user is not None and not user.is_verified:
        background_tasks.add_task(send_verification_email, user.email, user.username)

    return {"message": "If that address needs verification, a new link is on its way."}


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


@router.post("/forgot-password", status_code=status.HTTP_202_ACCEPTED)
async def forgot_password(
    body: PasswordResetRequest, session: SessionDep, background_tasks: BackgroundTasks
) -> dict[str, str]:
    """Start a password reset by emailing a one-time link.

    Replies the same way for every address, registered or not - otherwise this
    endpoint would happily tell an attacker which emails have accounts.
    """
    user = await user_service.get_user_by_email(session, body.email)
    if user is not None and user.is_active:
        background_tasks.add_task(
            send_password_reset_email, user.email, user.username, user.hashed_password
        )

    return {"message": "If that address has an account, a reset link is on its way."}


@router.post("/reset-password")
async def reset_password(body: PasswordResetConfirm, session: SessionDep) -> dict[str, str]:
    """Set a new password using the token from the emailed link.

    A single generic failure covers every reason a token might be unusable - expired,
    forged, already used, wrong purpose - because distinguishing them would only help
    someone probing for a token that still works.
    """
    succeeded = await user_service.reset_password(session, body.token, body.new_password)
    if not succeeded:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This reset link is invalid, expired, or has already been used.",
        )

    return {"message": "Password updated. You have been signed out on all devices."}


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    token: Annotated[str, Depends(oauth2_scheme)],
    _user: CurrentUserDep,
) -> None:
    """Revoke the token used to make this request.

    A JWT can't be "deleted" - it's just a signed string the client holds, and the
    server keeps no record of it. So instead we remember that this one is no longer
    acceptable, until the moment it would have expired on its own.

    Requiring CurrentUserDep means only a currently valid token can be revoked, so
    nobody can flood Redis by posting junk here.
    """
    payload = decode_access_token(token)
    if payload is None:  # pragma: no cover - CurrentUserDep already validated it
        return

    jti = payload.get("jti")
    exp = payload.get("exp")
    if jti is None or exp is None:
        return

    # Keep the blacklist entry only for the token's remaining lifetime.
    remaining = int(exp - datetime.now(timezone.utc).timestamp())
    await blacklist_token(jti, remaining)


@router.get("/me", response_model=UserRead)
async def read_current_user(current_user: CurrentUserDep) -> User:
    """Return the signed-in user's own profile.

    The body is a single line because CurrentUserDep already did the work: extracted
    the token, verified its signature and expiry, loaded the user, and checked the
    account is active. This is the pattern every protected endpoint will follow.
    """
    return current_user
