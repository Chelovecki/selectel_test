from fastapi import Request
from fastapi.responses import JSONResponse

from app.exceptions import VacancyExternalIdExistsError


async def vacancy_external_id_exists_handler(request: Request, exc: VacancyExternalIdExistsError):
    return JSONResponse(
        status_code=400,
        content={
            "error": "vacancy_external_id_exists_handler",
            "msg": f"Vacancy with external_id '{exc.external_id}' already exists",
        },
    )
