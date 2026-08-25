from fastapi import status


class GamerZoneError(Exception):
    """Base class for anything the application deliberately rejects.

    Services raise these instead of HTTPException so they stay free of HTTP concepts -
    the same function can then be called from a CLI command or a background job where
    status codes would be meaningless. A single handler in main.py turns them into
    responses.

    `status_code` is the HTTP mapping (used only by that handler), `code` is a stable
    machine-readable identifier for clients to branch on, and `detail` is the sentence
    shown to a person.
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
    """Raised when the database's unique constraint rejects a signup that passed our
    own checks - i.e. two identical registrations raced each other."""

    status_code = status.HTTP_409_CONFLICT
    code = "account_already_exists"
    detail = "An account with this email or username already exists."


class InvalidTokenError(GamerZoneError):
    """One message for expired, forged, already-used and wrong-purpose tokens alike,
    so the response can't be used to work out which one still has a chance."""

    status_code = status.HTTP_400_BAD_REQUEST
    code = "invalid_token"
    detail = "This link is invalid, expired, or has already been used."
