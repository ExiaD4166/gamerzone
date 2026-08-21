from sqlmodel import SQLModel


class Token(SQLModel):
    """The login response. Field names are fixed by the OAuth2 spec, which is why
    it's `access_token`/`token_type` rather than anything we'd have picked."""

    access_token: str
    token_type: str = "bearer"
