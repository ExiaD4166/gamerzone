from fastapi import status


class GamerZoneError(Exception):
    """Base class for anything the application deliberately rejects.

    Services raise these instead of HTTPException, so the same function works from a
    CLI command or a background job. A handler in main.py maps them to responses.

    `code` is a stable identifier for clients to branch on; `detail` is for a person.
    """

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    code: str = "error"
    detail: str = "Something went wrong."

    def __init__(self, detail: str | None = None) -> None:
        if detail is not None:
            self.detail = detail
        super().__init__(self.detail)


class EmailAlreadyExistsError(GamerZoneError):
    status_code = status.HTTP_409_CONFLICT
    code = "email_already_exists"
    detail = "An account with this email already exists."


class UsernameAlreadyTakenError(GamerZoneError):
    status_code = status.HTTP_409_CONFLICT
    code = "username_already_taken"
    detail = "This username is already taken."


class AccountAlreadyExistsError(GamerZoneError):
    """The UNIQUE constraint rejected a signup that passed our own checks - two
    identical registrations raced each other."""

    status_code = status.HTTP_409_CONFLICT
    code = "account_already_exists"
    detail = "An account with this email or username already exists."


class InvalidTokenError(GamerZoneError):
    """One message for expired, forged, already-used and wrong-purpose alike, so the
    response can't be used to work out which one still has a chance."""

    status_code = status.HTTP_400_BAD_REQUEST
    code = "invalid_token"
    detail = "This link is invalid, expired, or has already been used."
