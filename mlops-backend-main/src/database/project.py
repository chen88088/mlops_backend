from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from .base import Base, EntityRepository
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, unique=True, index=True)
    name = Column(String)
    create_time = Column(String)
    mlflow_experiment_id = Column(String)
    test_mlflow_experiment_id = Column(String)

    pipelines = relationship("Pipeline", back_populates="project")


class ProjectRepository(EntityRepository):
    def __init__(self):
        super().__init__(Project)