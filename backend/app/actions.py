from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app import models, schemas, utils


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_id(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


def get_users(db: Session, page: int = 1, page_size: int = 100):
    return db.query(models.User).order_by(models.User.id).offset((page - 1) * page_size).limit(page_size).all()


def create_user(db: Session, user: schemas.CreateUser):
    user.password = utils.hash_password(user.password)
    db_user = models.User(**user.dict())
    db.add(db_user)
    commit(db)
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user: schemas.UpdateUser):
    user.password = utils.hash_password(
        user.password) if user.password is not None else None
    db_user = get_user_by_id(db, user_id)
    for attr, value in user.dict().items():
        if value is not None:
            setattr(db_user, attr, value)

    commit(db)


def delete_user(db: Session, user_id: int):
    db_user = get_user_by_id(db, user_id)
    db.delete(db_user)
    commit(db)


def commit(db: Session):
    try:
        db.commit()
    except IntegrityError:
        raise HTTPException(status_code=400, detail="Entity already exists")
