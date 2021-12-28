from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app import config
from app.actions import get_user_by_username
from app.database import SessionLocal

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


async def db():
    sess = SessionLocal()
    try:
        yield sess
    finally:
        sess.close()


async def current_user(token: str = Depends(oauth2_scheme), sess: Session = Depends(db)):
    """
    Проверяет наличие и валидность токена указанного в заголовке Authorization
    """
    try:
        data = jwt.decode(token, config.SECRET_KEY, algorithms=[config.TOKEN_ALGORITHM])
        uname = data.get("sub")
        if uname is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        else:
            user = get_user_by_username(sess, uname)
            if user is None:
                raise HTTPException(status_code=401, detail="Invalid credentials")
            return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid credentials")
