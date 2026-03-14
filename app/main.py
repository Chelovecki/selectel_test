import logging
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager

from app.api.v1.router import api_router
from app.core.logging import setup_logging
from app.db.session import async_session_maker
from app.exception_handlers import vacancy_external_id_exists_handler
from app.exceptions import VacancyExternalIdExistsError
from app.services.parser import parse_and_store
from app.services.scheduler import create_scheduler

logger = logging.getLogger(__name__)

app = FastAPI(title="Selectel Vacancies API")

# подключение роутеров
app.include_router(api_router)

# подключение обработчика исключений 
app.add_exception_handler(VacancyExternalIdExistsError,
                          vacancy_external_id_exists_handler)

setup_logging()

_scheduler = None


async def _run_parse_job() -> None:
    try:
        async with async_session_maker() as session:
            await parse_and_store(session)
    except Exception as exc:
        logger.exception("Ошибка фонового парсинга: %s", exc)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Запуск приложения")
    await _run_parse_job()
    global _scheduler
    _scheduler = create_scheduler(_run_parse_job)
    _scheduler.start()

    yield  # возвращаем управление FastAPI

    logger.info("Остановка приложения")
    if _scheduler:
        _scheduler.shutdown(wait=False)
