from uuid import uuid4
from pydantic import BaseModel


class OrmModel(BaseModel):
    class Config:
        orm_mode = True

def create_uuid():
    return uuid4().hex