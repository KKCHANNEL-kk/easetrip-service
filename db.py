import os
from abc import ABC, abstractmethod
from pymongo import MongoClient
from sqlalchemy.orm import sessionmaker, Session
import aioredis


class DB(ABC):
    @abstractmethod
    def get_connection(self):
        pass


class Mongo(DB):
    host = os.getenv("MONGO_HOST")
    user = os.getenv("MONGO_USER")
    password = os.getenv("MONGO_PASSWORD")
    uri = f"mongodb+srv://{user}:{password}@{host}/?retryWrites=true&w=majority"
    database = "easetrip"

    def get_connection(self) -> MongoClient:
        from pymongo.mongo_client import MongoClient
        client = MongoClient(self.uri)[self.database]
        return client


class AMZRDS(DB):
    host = os.getenv("AMZRDS_HOST")
    user = os.getenv("AMZRDS_USER")
    password = os.getenv("AMZRDS_PASSWORD")
    database = "easetrip"
    port = 3306
    uri = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"

    def __init__(self) -> None:
        self.host = os.getenv("AMZRDS_HOST")
        self.user = os.getenv("AMZRDS_USER")
        self.password = os.getenv("AMZRDS_PASSWORD")
        self.database = "easetrip"
        self.port = 3306
        self.uri = f"mysql+pymysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
        connect_args = {"connect_timeout": 60}
        try:
            from sqlalchemy import create_engine
            self.engine = create_engine(self.uri,
                                        pool_size=20,
                                        pool_recycle=3600,
                                        pool_timeout=15,
                                        max_overflow=2,
                                        connect_args=connect_args)
        except Exception as e:
            print("Error connecting to MySQL DB:", e)

    def get_connection(self) -> Session:
        SessionLocal = sessionmaker(
                autocommit=False, autoflush=False, bind=self.engine)
        conn = SessionLocal()
        try:
            yield conn
        finally:
            conn.close()
