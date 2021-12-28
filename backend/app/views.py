from datetime import timedelta
import json
from typing import List
from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy.orm import Session
import asyncio
import aiohttp

from app import schemas, actions, dependencies, utils, config, models

router = APIRouter()


@router.post('/login')
async def login(credentials: schemas.AuthCredentials, sess=Depends(dependencies.db)):
    """
    Метод получения токена для аутентификации пользователя выполняющего запросы на защищенные эндпоинты

    Проверяет предоставленные данные (имя пользователя и пароль) и генерирует временный JWT токен
    """
    user = actions.get_user_by_username(sess, credentials.username)

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if not utils.check_password(user.password, credentials.password):
        raise HTTPException(status_code=401, detail="Wrong password")

    expiration_time = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = utils.create_token(
        data={"sub": user.username}, expires=expiration_time)
    return {"token": token}


@router.get('/users', response_model=List[schemas.User])
async def get_users(page: int = 1,
                    page_size: int = 100,
                    _: models.User = Depends(dependencies.current_user),
                    sess=Depends(dependencies.db)):
    """
    Метод получения отсортированного по ID списка пользователей
    Использует пагинацию
    Требует аутентификацию
    """
    users = actions.get_users(sess, page, page_size)
    return users


@router.post('/users', response_model=schemas.User)
async def create_user(new_user: schemas.CreateUser,
                      user: models.User = Depends(dependencies.current_user),
                      sess: Session = Depends(dependencies.db)):
    """
    Метод создает нового пользователя
    Требует аутентификацию и наличие rw прав у текущего пользователя
    """
    check_write_permissions(user)

    created = actions.create_user(sess, new_user)
    return created


@router.put('/users/{user_id}')
async def update_user(user_id: int,
                      updated_user: schemas.UpdateUser,
                      user: models.User = Depends(dependencies.current_user),
                      sess: Session = Depends(dependencies.db)):
    """
    Метод обновления пользователя
    Заменяет данные в БД на данные переданные в теле запроса
    Требует аутентификацию и наличие rw прав
    """
    check_write_permissions(user)
    actions.update_user(sess, user_id, updated_user)
    return {"status": "ok"}


@router.delete('/users/{user_id}')
async def delete_user(user_id: int,
                      user: models.User = Depends(dependencies.current_user),
                      sess: Session = Depends(dependencies.db)):
    """
    Метод удаления пользователя
    Требует аутентификацию и наличие rw прав
    """
    check_write_permissions(user)
    actions.delete_user(sess, user_id)
    return {"status": "ok"}


def check_write_permissions(user: models.User):
    """
    Функция проверяет, может ли пользователь вносить изменения в данные, и если нет - то возвращает ошибку
    """
    if not user.is_rw:
        raise HTTPException(403, detail="Insufficient permissions")


async def get_source(sess: aiohttp.ClientSession, source_number: int):
    """
    Функция получения данных от источника с указанным номером
    """
    try:

        async with sess.get(f"{config.EXTERNAL_API_URL}/source{source_number}.json") as resp:
            source_text = await resp.text()
            source_data = json.loads(source_text)

    except json.JSONDecodeError:
        source_data = []
    except asyncio.TimeoutError:
        source_data = []

    return source_data


@router.get('/external')
async def get_external_data():
    """
    Метод получения отсортированных данных из трех удаленных источников
    """
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=2)) as session:
        combined_data = await asyncio.gather(
            get_source(session, 1),
            get_source(session, 2),
            get_source(session, 3),
        )

        # Можно использовать знания о распределении id между источниками для оптимизации сортировки,
        # т.е. можно отсортировать данные каждого источника а потом соединить, т.к. нам известно где какие ID
        # но в целях упрощения сделана обычная сортировка по итоговому массиву данных от всех источников
        return sorted([inner for outer in combined_data for inner in outer], key=lambda x: x['id'])
