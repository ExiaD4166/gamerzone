from app.models.download_item import DownloadItem  # noqa: F401
from app.models.user import User  # noqa: F401

# Every SQLModel(table=True) class must be imported somewhere before Alembic runs,
# so SQLModel.metadata knows the table exists and autogenerate can see it.
# Importing all table models here, in one place, means that's guaranteed regardless
# of what order the rest of the app happens to import things in.
