from pydantic import Field
from .base import create_uuid, OrmModel
from typing import Optional


class Project(OrmModel):
    id: str = Field(default_factory=create_uuid)
    name: str
    create_time: Optional[str]
    mlflow_experiment_id: str
    test_mlflow_experiment_id: str
