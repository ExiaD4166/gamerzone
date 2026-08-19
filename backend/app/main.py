from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings

app = FastAPI(title=settings.app_name, version=settings.app_version)

app.include_router(api_router)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "GamerZone API is running. Visit /docs for the interactive API docs."}
