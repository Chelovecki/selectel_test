from typing import Iterable, List, Optional, AsyncGenerator

from sqlalchemy.exc import IntegrityError
from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session_maker
from app.exceptions import VacancyExternalIdExistsError
from app.models.vacancy import Vacancy
from app.schemas.vacancy import VacancyCreate, VacancyUpdate


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_vacancy(session: AsyncSession, vacancy_id: int) -> Optional[Vacancy]:
    result = await session.execute(select(Vacancy).where(Vacancy.id == vacancy_id))
    return result.scalar_one_or_none()





async def list_vacancies(
    session: AsyncSession,
    timetable_mode_name: Optional[str],
    city_name: Optional[str],
) -> List[Vacancy]:
    stmt: Select = select(Vacancy)
    if timetable_mode_name:
        stmt = stmt.where(Vacancy.timetable_mode_name.ilike(
            f"%{timetable_mode_name}%"))
    if city_name:
        stmt = stmt.where(Vacancy.city_name.ilike(f"%{city_name}%"))
    stmt = stmt.order_by(Vacancy.published_at.desc())
    result = await session.execute(stmt)
    return list(result.scalars().all())




async def create_vacancy(session: AsyncSession, data: VacancyCreate) -> Vacancy:
    vacancy = Vacancy(**data.model_dump())
    session.add(vacancy)
    try:
        await session.commit()
    except IntegrityError as exc:
        await session.rollback()
        if data.external_id is not None:
            raise VacancyExternalIdExistsError(external_id=data.external_id) from exc
        raise
    await session.refresh(vacancy)
    return vacancy



async def update_vacancy(
    session: AsyncSession, vacancy: Vacancy, data: VacancyUpdate
) -> Vacancy:
    vacancy_data = data.model_dump()
    for field, value in vacancy_data.items():
        if field == "external_id":
            stmt = select(Vacancy).where(Vacancy.external_id == value)
            res = await session.execute(stmt)
            res = res.scalar_one_or_none()
            if res is not None and res.id != vacancy.id:
                raise VacancyExternalIdExistsError(external_id=value)

        setattr(vacancy, field, value)
    await session.commit()
    await session.refresh(vacancy)
    return vacancy


async def delete_vacancy(session: AsyncSession, vacancy: Vacancy) -> None:
    await session.delete(vacancy)
    await session.commit()


async def upsert_external_vacancies(
    session: AsyncSession, payloads: Iterable[dict]
) -> int:
    payloads = list(payloads)

    external_ids = [
        payload["external_id"]
        for payload in payloads
        if payload["external_id"] is not None
    ]

    if external_ids:
        existing_result = await session.execute(
            select(Vacancy.external_id).where(Vacancy.external_id.in_(external_ids))
        )
        existing_ids = set(existing_result.scalars().all())
    else:
        existing_ids = set()

    created_count = 0
    for payload in payloads:
        ext_id = payload["external_id"]
        if ext_id is not None and ext_id in existing_ids:
            result = await session.execute(
                select(Vacancy).where(Vacancy.external_id == ext_id)
            )
            vacancy = result.scalar_one()
            for field, value in payload.items():
                setattr(vacancy, field, value)
        else:
            session.add(Vacancy(**payload))
            created_count += 1

    await session.commit()
    return created_count
