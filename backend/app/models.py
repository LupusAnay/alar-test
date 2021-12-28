from sqlalchemy import Column, Integer, String, Boolean, LargeBinary

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(LargeBinary)
    is_rw = Column(Boolean, default=False)
