from fastapi import APIRouter

api_router = APIRouter(prefix="/api/v1")


@api_router.get("/health")
def health_check() -> dict[str, str]:
    """Trivial liveness check: if this responds, the server process is up."""
    return {"status": "ok"}


@api_router.get("/greet/{username}")
def greet_user(username: str, loud: bool = False) -> dict[str, str]:
    """
    Demonstrates a required path parameter (`username`) and an optional query
    parameter (`loud`). FastAPI reads these type hints to validate incoming
    requests and to generate the interactive docs at /docs.
    """
    message = f"Welcome to GamerZone, {username}!"
    if loud:
        message = message.upper()
    return {"message": message}
