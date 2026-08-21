from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.api.deps import CurrentUserDep, SessionDep, SuperUserDep
from app.models.download_item import (
    DownloadItem,
    DownloadItemCreate,
    DownloadItemRead,
    DownloadItemUpdate,
)

router = APIRouter(prefix="/downloads", tags=["downloads"])

# Access model: any signed-in member may read the links (this is the members-only
# download page), but only administrators may add, edit or remove them.
# Declaring CurrentUserDep/SuperUserDep is enough - FastAPI resolves the dependency
# and rejects the request before the function body ever runs.


@router.post("/", response_model=DownloadItemRead, status_code=status.HTTP_201_CREATED)
async def create_download_item(
    item_in: DownloadItemCreate, session: SessionDep, _admin: SuperUserDep
) -> DownloadItem:
    item = DownloadItem.model_validate(item_in)
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


@router.get("/", response_model=list[DownloadItemRead])
async def list_download_items(session: SessionDep, _user: CurrentUserDep) -> list[DownloadItem]:
    result = await session.exec(select(DownloadItem))
    return list(result.all())


@router.get("/{item_id}", response_model=DownloadItemRead)
async def get_download_item(item_id: int, session: SessionDep, _user: CurrentUserDep) -> DownloadItem:
    item = await session.get(DownloadItem, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Download item not found")
    return item


@router.patch("/{item_id}", response_model=DownloadItemRead)
async def update_download_item(
    item_id: int, item_in: DownloadItemUpdate, session: SessionDep, _admin: SuperUserDep
) -> DownloadItem:
    item = await session.get(DownloadItem, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Download item not found")

    update_data = item_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)

    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_download_item(item_id: int, session: SessionDep, _admin: SuperUserDep) -> None:
    item = await session.get(DownloadItem, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Download item not found")
    await session.delete(item)
    await session.commit()
