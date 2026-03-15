from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.vacancy import (
    create_vacancy,
    delete_vacancy,
    get_session,
    get_vacancy,
    list_vacancies,
    update_vacancy,
)
from app.schemas.vacancy import VacancyCreate, VacancyRead, VacancyUpdate
from app.constants import VACANCY_EXTERNAL_ID_EXISTS_RESPONSE


router = APIRouter(prefix="/vacancies", tags=["vacancies"])


@router.get("/", response_model=List[VacancyRead])
async def list_vacancies_endpoint(
    timetable_mode_name: Optional[str] = None,
    city: Optional[str] = None,
    session: AsyncSession = Depends(get_session),
) -> List[VacancyRead]:
    return [
        VacancyRead.model_validate(vacancy)
        for vacancy in await list_vacancies(session, timetable_mode_name, city)
    ]


@router.get("/{vacancy_id}", response_model=VacancyRead)
async def get_vacancy_endpoint(
    vacancy_id: int, session: AsyncSession = Depends(get_session)
) -> VacancyRead:
    vacancy = await get_vacancy(session, vacancy_id)
    if not vacancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    return vacancy


@router.post(
    "/",
    response_model=VacancyRead,
    status_code=status.HTTP_201_CREATED,
    responses={**VACANCY_EXTERNAL_ID_EXISTS_RESPONSE},
)
async def create_vacancy_endpoint(
    payload: VacancyCreate, session: AsyncSession = Depends(get_session)
) -> VacancyRead:
    return VacancyRead.model_validate(await create_vacancy(session, payload))


@router.put(
    "/{vacancy_id}",
    response_model=VacancyRead,
    responses={**VACANCY_EXTERNAL_ID_EXISTS_RESPONSE}
)
async def update_vacancy_endpoint(
    vacancy_id: int,
    payload: VacancyUpdate,
    session: AsyncSession = Depends(get_session),
) -> VacancyRead:
    vacancy = await get_vacancy(session, vacancy_id)
    if not vacancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    return VacancyRead.model_validate(await update_vacancy(session, vacancy, payload))


@router.delete("/{vacancy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vacancy_endpoint(
    vacancy_id: int, session: AsyncSession = Depends(get_session)
) -> None:
    vacancy = await get_vacancy(session, vacancy_id)
    if not vacancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Not found")
    await delete_vacancy(session, vacancy)
