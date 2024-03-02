from fastapi import HTTPException
from sqlalchemy import Column, String, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .base import Base, EntityRepository
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class Pipeline(Base):
    __tablename__ = "pipelines"

    id = Column(String, primary_key=True, unique=True, index=True)
    project_id = Column(String, ForeignKey("projects.id"))
    type = Column(String)
    repository_id = Column(Integer)
    storage_bucket = Column(String)
    data_version_bucket = Column(String)
    test_storage_bucket = Column(String)
    test_data_version_bucket = Column(String)

    project = relationship("Project", back_populates="pipelines")
    pipeline_APIs = relationship("PipelineAPI", back_populates="pipeline")
    pipeline_Jobs = relationship("PipelineJob", back_populates="pipeline")
    run_Infos = relationship("RunInfo", back_populates="pipeline")


class PipelineRepository(EntityRepository):
    def __init__(self):
        super().__init__(Pipeline)
    
    def _create_specific_type(self, pipeline: Pipeline, type: str):
        pipeline.type = type
        return self.create(pipeline)
    
    def _read_specific_type(self, project_id: str, type: str):
        try:
            pipeline = self.session.query(self.entity).filter(
                self.entity.project_id == project_id, self.entity.type == type).first()
            logger.debug(
                f'Read {type} pipeline in project "id={project_id}" in SQL success.')
        except Exception as e:
            logger.error(
                f'Read {type} pipeline in project "id={project_id}" in SQL fail.\n{e}')
            raise HTTPException(
                status_code=404,
                detail=f'Read {type} {self.entity.__name__} fail.',
            )
        return pipeline

    def create_training(self, pipeline: Pipeline):
        return self._create_specific_type(pipeline, "training")
    
    def read_training(self, project_id: str):
        return self._read_specific_type(project_id, "training")

    def create_inference(self, pipeline: Pipeline):
        return self._create_specific_type(pipeline, "inference")
    
    def read_inference(self, project_id: str):
        return self._read_specific_type(project_id, "inference")

    def read_all_by_project_id(self, project_id: str):
        try:
            pipelines = self.session.query(self.entity).filter(
                self.entity.project_id == project_id).all()
            logger.debug(
                f'Read all pipelines in project "id={project_id}" in SQL success.')
        except Exception as e:
            logger.error(
                f'Read all pipelines in project "id={project_id}" in SQL fail.\n{e}')
            raise HTTPException(
                status_code=404,
                detail=f'Read all {self.entity.__name__} fail.',
            )
        return pipelines


class PipelineJob(Base):
    __tablename__ = "pipelineJobs"

    id = Column(String, primary_key=True, unique=True, index=True)
    pipeline_id = Column(String, ForeignKey("pipelines.id"))
    order = Column(Integer)
    name = Column(String)
    os = Column(String)
    image = Column(String)
    runner_tag = Column(String)

    pipeline = relationship("Pipeline", back_populates="pipeline_Jobs")


class PipelineJobRepository(EntityRepository):
    def __init__(self):
        super().__init__(PipelineJob)

    def read_all_by_pipeline_id(self, pipeline_id: str):
        try:
            pipelineJobs = self.session.query(self.entity).filter(
                self.entity.pipeline_id == pipeline_id).all()
            logger.debug(
                f'Read all pipelineJobs in pipeline "id={pipeline_id}" in SQL success.')
        except Exception as e:
            logger.error(
                f'Read all pipelineJobs in pipeline "id={pipeline_id}" in SQL fail.\n{e}')
            raise HTTPException(
                status_code=404,
                detail=f'Read all {self.entity.__name__} fail.',
            )
        return pipelineJobs


class PipelineAPI(Base):
    __tablename__ = "pipelineAPIs"

    id = Column(String, primary_key=True, unique=True, index=True)
    pipeline_id = Column(String, ForeignKey("pipelines.id"))
    name = Column(String)
    type = Column(String)
    flow_control = Column(JSON)
    test_repository_id = Column(Integer)

    pipeline = relationship("Pipeline", back_populates="pipeline_APIs")
    pipeline_Runs = relationship("PipelineRun", back_populates="pipelineAPI")
    test_Run_Infos = relationship("TestRunInfo", back_populates="pipelineAPI")


class PipelineAPIRepository(EntityRepository):
    def __init__(self):
        super().__init__(PipelineAPI)

    def read_all_by_pipeline_id(self, pipeline_id: str):
        try:
            pipelineJobs = self.session.query(self.entity).filter(
                self.entity.pipeline_id == pipeline_id).all()
            logger.debug(
                f'Read all pipelineAPIs in pipeline "id={pipeline_id}" in SQL success.')
        except Exception as e:
            logger.error(
                f'Read all pipelineAPIs in pipeline "id={pipeline_id}" in SQL fail.\n{e}')
            raise HTTPException(
                status_code=404,
                detail=f'Read all {self.entity.__name__} fail.',
            )
        return pipelineJobs

    def create_default(self, api: PipelineAPI):
        api.type = "Default"
        return self.create(api)

    def create_custom(self, api: PipelineAPI):
        api.type = "Custom"
        return self.create(api)

    def read_default(self, pipeline_id: str):
        try:
            pipelineAPI = self.session.query(self.entity).filter(
                self.entity.pipeline_id == pipeline_id, self.entity.type == 'Default').first()
            logger.debug(
                f'Read default pipelineAPI in pipeline "id={pipeline_id}" in SQL success.')
        except Exception as e:
            logger.error(
                f'Read default pipelineAPI in pipeline "id={pipeline_id}" in SQL fail.\n{e}')
            raise HTTPException(
                status_code=404,
                detail=f'Read all {self.entity.__name__} fail.',
            )
        return pipelineAPI
    
    def read_customs(self, pipeline_id: str):
        try:
            pipelineAPIs = self.session.query(self.entity).filter(
                self.entity.pipeline_id == pipeline_id, self.entity.type == 'Custom').all()
            logger.debug(
                f'Read custom pipelineAPIs in pipeline "id={pipeline_id}" in SQL success.')
        except Exception as e:
            logger.error(
                f'Read custom pipelineAPIs in pipeline "id={pipeline_id}" in SQL fail.\n{e}')
            raise HTTPException(
                status_code=404,
                detail=f'Read all {self.entity.__name__} fail.',
            )
        return pipelineAPIs
