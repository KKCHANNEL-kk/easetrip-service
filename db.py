import os
from abc import ABC, abstractmethod
from typing import Generator
from sqlalchemy.orm import sessionmaker, Session
from pymongo.mongo_client import MongoClient
from pymongo.database import Database as MongoDatabase


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

    def get_connection(self) -> MongoDatabase:
        client: MongoClient = MongoClient(Mongo.uri)
        db: MongoDatabase = client[Mongo.database]

        return db

    def __repr__(self) -> str:
        res = f"MongoDB: \n\
        host: {self.host}\n\
        database: {self.database}\n\
        uri: {self.uri}"
        return res
        

class AMZRDS(DB):
    host = os.getenv("AMZRDS_HOST")
    user = os.getenv("AMZRDS_USER")
    password = os.getenv("AMZRDS_PASSWORD")
    database = "easetrip"
    port = 3306
    uri = f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"

    def __init__(self) -> None:
        connect_args = {"connect_timeout": 60}
        try:
            from sqlalchemy import create_engine
            self.engine = create_engine(AMZRDS.uri,
                                        pool_size=20,
                                        pool_recycle=3600,
                                        pool_timeout=15,
                                        max_overflow=2,
                                        connect_args=connect_args)
        except Exception as e:
            print("Error connecting to MySQL DB:", e)

    def get_connection(self) -> Generator[Session,None,None]:
        SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine)
        conn: Session = SessionLocal()
        try:
            yield conn
        finally:
            conn.close()

    def __repr__(self) -> str:
        res = f"AMZRDS: \n\
        host: {self.host}\n\
        database: {self.database}\n\
        uri: {self.uri}"
        return res