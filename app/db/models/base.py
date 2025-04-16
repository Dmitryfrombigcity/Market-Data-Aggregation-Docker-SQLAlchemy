from sqlalchemy.orm import DeclarativeBase, declared_attr

from app.utils.case_converter import camel_case_to_snake_case


class Base(DeclarativeBase):
    __abstract__ = True

    @classmethod
    @declared_attr  # type: ignore
    def __tablename__(cls) -> str:
        return camel_case_to_snake_case(cls.__name__)
