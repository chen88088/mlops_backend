import os 
import logging
from config import Setting
from fastapi import HTTPException

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, database_exists
from contextlib import contextmanager


logger = logging.getLogger()
logger.setLevel(logging.INFO)
# SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
setting = Setting()
db_user = os.environ["DB_USER"]
db_password = os.environ["DB_PASSWORD"]
# Create for mlflow
SQLALCHEMY_DATABASE_URL = f"postgresql://{setting.db_user}:{setting.db_password}@{setting.db_url}/mlflow"
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_size=50, max_overflow=0)
if not database_exists(engine.url):
    try:
        create_database(engine.url)
        logger.debug("Create database 'mlflow' success.")
    except Exception as e:
        logger.error(f"Create database 'mlflow' fail.\n{e}")
# Create for mlops
SQLALCHEMY_DATABASE_URL = f"postgresql://{setting.db_user}:{setting.db_password}@{setting.db_url}/mlops"
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_size=50, max_overflow=0, pool_pre_ping=True)
if not database_exists(engine.url):
    try:
        create_database(engine.url)
        logger.debug("Create database 'mlops' success.")
    except Exception as e:
        logger.error(f"Create database 'mlops' fail.\n{e}")


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class EntityRepository:
    def __init__(self, entity):
        self.entity = entity
        self.session = SessionLocal()
    
    def __del__(self):
        self.session.close()

    def create(self, instance):
        try:
            self.session.add(instance)
            self.session.commit()
            self.session.refresh(instance)
            logger.debug(f'Create new {self.entity.__name__} in SQL success.')
        except Exception as e:
            logger.error(f'Create new {self.entity.__name__} in SQL fail.\n{e}')
            raise HTTPException(
                status_code=404,
                detail=f"Create {self.entity.__name__} fail.",
            )
        return instance

    def read_first(self, id: str):
        try:
            model = self.session.query(self.entity).filter(self.entity.id == id).first()
            logger.debug(f'Get first {self.entity.__name__} in SQL success.')
        except Exception as e:
            logger.error(f'Get first {self.entity.__name__} in SQL fail.\n{e}')
            raise HTTPException(
                status_code=404,
                detail=f'Read {self.entity.__name__} fail.',
            )
        return model

    def read_all(self):
        try:
            model = self.session.query(self.entity).filter().all()
            logger.debug(f'Get all {self.entity.__name__} in SQL success.')
        except Exception as e:
            logger.error(f'Get all {self.entity.__name__} in SQL fail.\n{e}')
            raise HTTPException(
                status_code=404,
                detail=f'Read all {self.entity.__name__} fail.',
            )
        return model

    def update(self, instance):
        model = self.read_first(instance.id)
        for key in vars(model):
            if key.startswith('_'):
                continue
            setattr(model, key, getattr(instance, key))
        try:
            #result = self.session.query(self.entity).filter(self.entity.id == instance.id).update(instance)
            self.session.commit()
            logger.debug(f'Update {self.entity.__name__} "id={instance.id}" in SQL success.')
        except Exception as e:
            logger.error(f'Update {self.entity.__name__} "id={instance.id}" in SQL fail.\n{e}')
            raise HTTPException(
                status_code=404,
                detail=f'Update {self.entity.__name__} fail.',
            )
        #return result

    def delete(self, id: str):
        try:
            result = self.session.query(self.entity).filter(self.entity.id == id).delete()
            self.session.commit()
            logger.debug(f'Delete {self.entity.__name__} in SQL success.')
        except Exception as e:
            logger.error(f'Delete {self.entity.__name__} in SQL fail.\n{e}')
            raise HTTPException(
                status_code=404,
                detail=f'Delete {self.entity.__name__} fail.',
            )
        return result