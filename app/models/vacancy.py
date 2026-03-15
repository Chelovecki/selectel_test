from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, Index, Integer, String, func, text
from sqlalchemy.orm import Mapped, mapped_column, validates

from app.db.base import Base


class Vacancy(Base):
    __tablename__ = "vacancies"
    __table_args__ = (
        Index('uq_vacancies_external_id',
              'external_id',
              unique=True,
              postgresql_where=text("external_id IS NOT NULL")),  
        CheckConstraint(
            'external_id IS NULL OR external_id >= 0',
            name='ck_vacancies_external_id_positive'),
    )
    

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    timetable_mode_name: Mapped[str] = mapped_column(String, nullable=False)
    tag_name: Mapped[str] = mapped_column(String, nullable=False)
    city_name: Mapped[str | None] = mapped_column(String, nullable=True)
    published_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False)
    is_remote_available: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False)
    is_hot: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
    )
    external_id: Mapped[int | None] = mapped_column(Integer, nullable=True)

    @validates('external_id')
    def validate_external_id(self, key, value):
        if value is not None and value < 0:
            raise ValueError("external_id must be >= 0")
        return value
