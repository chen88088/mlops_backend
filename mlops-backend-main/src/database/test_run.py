from fastapi import HTTPException
from sqlalchemy import Column, String, Boolean, ForeignKey, Integer
from sqlalchemy.orm import relationship
from .base import Base, EntityRepository
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TestRunInfo(Base):
    __tablename__ = "testRunInfos"

    id = Column(String, primary_key=True, unique=True, index=True)
    pipelineAPI_id = Column(String, ForeignKey("pipelineAPIs.id"))
    git_pipeline_id = Column(Integer)
    create_time = Column(String)
    finish_time = Column(String)

    testPipeline_Runs = relationship("TestPipelineRun", back_populates="testRunInfo")
    pipelineAPI = relationship("PipelineAPI", back_populates="test_Run_Infos")

class TestRunInfoRepository(EntityRepository):
    def __init__(self):
        super().__init__(TestRunInfo)

    def read_all_by_pipelineAPI_id(self, pipelineAPI_id: str):
        try:
            runInfos = self.session.query(self.entity).filter(
                self.entity.pipelineAPI_id == pipelineAPI_id).all()
            logger.debug(
                f'Read all testRunInfos in pipelineAPI "id={pipelineAPI_id}" in SQL success.')
        except Exception as e:
            logger.error(
                f'Read all testRunInfos in pipelineAPI "id={pipelineAPI_id}" in SQL fail.\n{e}')
            raise HTTPException(
                status_code=404,
                detail=f'Read all {self.entity.__name__} fail.',
            )
        return runInfos

class TestPipelineRun(Base):
    __tablename__ = "testPipelineRuns"

    id = Column(String, primary_key=True, unique=True, index=True)
    testRunInfo_id = Column(String, ForeignKey("testRunInfos.id"))
    git_pipeline_id = Column(Integer)
    mlflow_run_id = Column(String)
    create_time = Column(String)
    finish_time = Column(String)
    callback_url = Column(String)

    testRunInfo = relationship("TestRunInfo", back_populates="testPipeline_Runs")

class TestPipelineRunRepository(EntityRepository):
    def __init__(self):
        super().__init__(TestPipelineRun)
    
    def read_all_running_pipelines(self):
        try:
            pipelineJobs = self.session.query(self.entity).filter(
                self.entity.finish_time == None).all()
            logger.debug(
                f'Read running testPipelines in SQL success.')
        except Exception as e:
            logger.error(
                f'Read running testPipelines in SQL fail.\n{e}')
            raise HTTPException(
                status_code=404,
                detail=f'Read all {self.entity.__name__} fail.',
            )
        return pipelineJobs

    def read_all_by_testRunInfo_id(self, testRunInfo_id: str):
        try:
            pipelineRuns = self.session.query(self.entity).filter(
                self.entity.testRunInfo_id == testRunInfo_id).all()
            logger.debug(
                f'Read all testPipelineRuns in testRunInfo "id={testRunInfo_id}" in SQL success.')
        except Exception as e:
            logger.error(
                f'Read all testPipelineRuns in testRunInfo "id={testRunInfo_id}" in SQL fail.\n{e}')
            raise HTTPException(
                status_code=404,
                detail=f'Read all {self.entity.__name__} fail.',
            )
        return pipelineRuns
    '''
    def read_all_by_pipelineAPI_id(self, pipelineAPI_id: str):
        try:
            pipelineRuns = self.session.query(self.entity).filter(
                self.entity.pipelineAPI_id == pipelineAPI_id).all()
            logger.debug(
                f'Read all testPipelineRuns in pipelineAPI "id={pipelineAPI_id}" in SQL success.')
        except Exception as e:
            logger.error(
                f'Read all testPipelineRuns in pipelineAPI "id={pipelineAPI_id}" in SQL fail.\n{e}')
            raise HTTPException(
                status_code=404,
                detail=f'Read all {self.entity.__name__} fail.',
            )
        return pipelineRuns'''