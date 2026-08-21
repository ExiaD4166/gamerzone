from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from app.api.deps import SessionDep
from app.models.download_item import (
    DownloadItem,
    DownloadItemCreate,
    DownloadItemRead,
    DownloadItemUpdate,
)

router = APIRouter(prefix="/downloads", tags=["downloads"])

# NOTE: not login-protected yet - auth doesn't exist until Phase 3/4. These endpoints
# will move behind a `get_current_user` dependency once that lands (Phase 6).


@router.post("/", response_model=DownloadItemRead, status_code=status.HTTP_201_CREATED)
async def create_download_item(item_in: DownloadItemCreate, session: SessionDep) -> DownloadItem:
    item = DownloadItem.model_validate(item_in)
    session.add(item)
    await session.commit()
    await session.refresh(item)
    return item


@router.get("/", response_model=list[DownloadItemRead])
async def list_download_items(session: SessionDep) -> list[DownloadItem]:
    result = await session.exec(select(DownloadItem))
    return list(result.all())


@router.get("/{item_id}", response_model=DownloadItemRead)
async def get_download_item(item_id: int, session: SessionDep) -> DownloadItem:
    item = await session.get(DownloadItem, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Download item not found")
    return item


@router.patch("/{item_id}", response_model=DownloadItemRead)
async def update_download_item(item_id: int, item_in: DownloadItemUpdate, session: SessionDep) -> DownloadItem:
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
async def delete_download_item(item_id: int, session: SessionDep) -> None:
    item = await session.get(DownloadItem, item_id)
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Download item not found")
    await session.delete(item)
    await session.commit()
