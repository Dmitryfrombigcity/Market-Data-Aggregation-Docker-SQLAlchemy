from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base


class IdMixin:
    id: Mapped[int] = mapped_column(primary_key=True, sort_order=-1)
