from abc import abstractmethod
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base,DeclarativeMeta
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON, Date, Boolean, Numeric
from werkzeug.security import generate_password_hash, check_password_hash
from db import AMZRDS, Mongo
from pydantic import BaseModel as BaseType

Base: DeclarativeMeta = declarative_base()  # <-元类

# 用来加载抽象方法的基类


class ModelBase(Base):
    __abstract__ = True

    def create(self, db_type: str = 'mysql'):
        if db_type == 'mysql':
            conn = next(AMZRDS().get_connection())
            conn.add(self)
            try:
                conn.commit()
            except Exception as e:
                # Rollback the changes
                conn.rollback()
                print(e)
                # Re-raise the exception
                return e
            finally:
                conn.close()

    # 解 dict 为 model
    def __init__(self, *args, **kwargs):
        if args:
            data = args[0]
            if isinstance(data, dict):
                for key in data.keys():
                    setattr(self, key, data[key])
            else:
                for column in data.__table__.columns:
                    setattr(self, column.name, getattr(data, column.name))
        else:
            for key in kwargs.keys():
                setattr(self, key, kwargs[key])

    def __repr__(self) -> str:
        res: str = self.__tablename__ + ":\n"
        for column in self.__table__.columns:
            res += f"{column.name}: {getattr(self, column.name)}\n"
        return res


class Test(ModelBase):
    __tablename__ = 'test'
    id = Column(Integer, primary_key=True, autoincrement=True)
    val = Column(String(255), nullable=True)

    def __init__(self, val: str):
        self.val = val


class Schedule(ModelBase):
    __tablename__ = 'schedule'
    id = Column(String(255), primary_key=True)  # 和 Mongo 中 id 保持一致，uid-时间戳
    name = Column(String(255), nullable=False)
    uid = Column(String(255), nullable=False)  # Schedule的创建者id
    start_date = Column(Date)
    end_date = Column(Date)
    options = Column(JSON)

    json = Column(JSON)
    create_time = Column(DateTime, nullable=False, default=datetime.now())
    update_time = Column(DateTime, nullable=False, default=datetime.now())
    is_deleted = Column(Integer, nullable=False, default=0)
    is_finished = Column(Integer, nullable=False, default=0)

    def __init__(self, id, name, uid, start_date, end_date, options):
        self.id = id
        self.name = name
        self.uid = uid
        self.start_date = start_date
        self.end_date = end_date
        self.options = options


class Point(ModelBase):
    __tablename__ = 'point'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    longitude = Column(Numeric(10,7), nullable=False)
    latitude = Column(Numeric(10,7), nullable=False)
    address = Column(String(255), nullable=False)
    mapid = Column(String(255))
    city = Column(String(255))
    introduction = Column(Text)

    options = Column(JSON)  # pic, tag 塞这
    create_time = Column(DateTime, nullable=False, default=datetime.now())
    update_time = Column(DateTime, nullable=False, default=datetime.now())


class User(ModelBase):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    email = Column(String(100), unique=True, nullable=False)

    def __init__(self, username, password, email):
        self.username = username
        self.set_password(password)
        self.email = email

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str):
        return check_password_hash(str(self.password_hash), password)

    def create(self):
        conn = next(AMZRDS().get_connection())
        conn.add(self)
        try:
            conn.commit()
        except Exception as e:
            # Rollback the changes
            conn.rollback()
            # Re-raise the exception
            return e
        finally:
            conn.close()
