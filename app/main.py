from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app import models  # Добавляем как выглядит таблица для постов
from app.database import Base, engine  # Настройка подключений к БД
from app.routers import posts
from app.schemas import UserCreate, UserResponse

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="Blog API", lifespan=lifespan)

app.include_router(posts.router)  # + роутер (набора эндпоинтов) к приложению.

@app.post("/register", response_model=UserResponse, status_code=201)
def register_user(data: UserCreate):
    return {"email": data.email, "message": "Пользователь зарегистрирован"}




# Фронтенд: обычные HTML/CSS/JS из папки frontend, без сборки.
app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(FRONTEND_DIR / "index.html")



'''
Приложение стартурет отсюда, lifespan -это имя параметра конструктора FastAPI.
FastAPI ищет аргумент lifespan и вызывает переданную функцию при старте/остановке приложения.
lifespan регистрирует функцию, которую FastAPI вызовет один раз при старте приложения (до yield)
и один раз при остановке (после yield).


1. lifespan=lifespan → FastAPI запоминает функцию.
2. При запуске сервера FastAPI вызывает lifespan(app).
3. Внутри выполняется Base.metadata.create_all(bind=engine) → SQLAlchemy создаёт таблицы, зарегистрированные в Base.metadata
(Все таблицы попадают в Base.metadata. Posts попал благодаря "from app import models").
4. yield — приложение начинает принимать запросы.
5. При остановке выполнение продолжится после yield (там пусто — ничего не делается).

Почему create_all вообще нужен
create_all создаёт только отсутствующие таблицы.
Если таблица уже есть — он её не трогает и не обновляет схему (для миграций нужен Alembic).
Для учебного проекта — норм; для продакшена — обычно убирают из lifespan и используют миграции.

В продакшене create_all убирают, потому что он умеет только создавать таблицы с нуля
и не может изменять существующие (добавлять колонки, менять типы).
Для эволюции схемы используют Alembic — официальный инструмент миграций для SQLAlchemy .
'''
