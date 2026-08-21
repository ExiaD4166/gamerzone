from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.session import get_session

# Annotated[Type, Depends(...)] bundles "what you get" with "how to get it" into one
# reusable alias. Every endpoint that needs a database session just declares
# `session: SessionDep` instead of repeating Depends(get_session) everywhere.
# Shared dependencies live here so routers don't redefine them.
SessionDep = Annotated[AsyncSession, Depends(get_session)]
