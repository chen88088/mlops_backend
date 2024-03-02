from fastapi import HTTPException
from sqlalchemy import Column, String, Boolean, ForeignKey, Integer
from sqlalchemy.orm import relationship
from .base import Base, EntityRepository
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class RunInfo(Base):
    __tablename__ = "runInfos"

    id = Column(String, primary_key=True, unique=True, index=True)
    pipeline_id = Column(String, ForeignKey("pipelines.id"))
    create_time = Column(String)
    finish_time = Column(String)

    pipeline = relationship("Pipeline", back_populates="run_Infos")
    pipeline_Runs = relationship("PipelineRun", back_populates="runInfo")

class RunInfoRepository(EntityRepository):
    def __init__(self):
        super().__init__(RunInfo)

    def read_all_by_pipeline_id(self, pipeline_id: str):
        try:
            runInfos = self.session.query(self.entity).filter(
                self.entity.pipeline_id == pipeline_id).all()
            logger.debug(
                f'Read all runInfos in pipeline "id={pipeline_id}" in SQL success.')
        except Exception as e:
            logger.error(
                f'Read all runInfos in pipeline "id={pipeline_id}" in SQL fail.\n{e}')
            raise HTTPException(
                status_code=404,
                detail=f'Read all {self.entity.__name__} fail.',
            )
        return runInfos

class PipelineRun(Base):
    __tablename__ = "pipelineRuns"

    id = Column(String, primary_key=True, unique=True, index=True)
    runInfo_id = Column(String, ForeignKey("runInfos.id"))
    pipelineAPI_id = Column(String, ForeignKey("pipelineAPIs.id"))
    git_pipeline_id = Column(Integer)
    mlflow_run_id = Column(String)
    create_time = Column(String)
    finish_time = Column(String)
    callback_url = Column(String)

    runInfo = relationship("RunInfo", back_populates="pipeline_Runs")
    pipelineAPI = relationship("PipelineAPI", back_populates="pipeline_Runs")

class PipelineRunRepository(EntityRepository):
    def __init__(self):
        super().__init__(PipelineRun)
    
    def read_all_running_pipelines(self):
        try:
            pipelineJobs = self.session.query(self.entity).filter(
                self.entity.finish_time == None).all()
            logger.debug(
                f'Read running pipelines in SQL success.')
        except Exception as e:
            logger.error(
                f'Read running pipelines in SQL fail.\n{e}')
            raise HTTPException(
                status_code=404,
                detail=f'Read all {self.entity.__name__} fail.',
            )
        return pipelineJobs

    def read_all_by_runInfo_id(self, runInfo_id: str):
        try:
            pipelineRuns = self.session.query(self.entity).filter(
                self.entity.runInfo_id == runInfo_id).all()
            logger.debug(
                f'Read all pipelineRuns in runInfo "id={runInfo_id}" in SQL success.')
        except Exception as e:
            logger.error(
                f'Read all pipelineRuns in runInfo "id={runInfo_id}" in SQL fail.\n{e}')
            raise HTTPException(
                status_code=404,
                detail=f'Read all {self.entity.__name__} fail.',
            )
        return pipelineRuns

    def read_all_by_pipelineAPI_id(self, pipelineAPI_id: str):
        try:
            pipelineRuns = self.session.query(self.entity).filter(
                self.entity.pipelineAPI_id == pipelineAPI_id).all()
            logger.debug(
                f'Read all pipelineRuns in pipelineAPI "id={pipelineAPI_id}" in SQL success.')
        except Exception as e:
            logger.error(
                f'Read all pipelineRuns in pipelineAPI "id={pipelineAPI_id}" in SQL fail.\n{e}')
            raise HTTPException(
                status_code=404,
                detail=f'Read all {self.entity.__name__} fail.',
            )
        return pipelineRuns