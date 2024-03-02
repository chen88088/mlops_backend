from src import gitlab_proxy as gitlab
from src import database, schema, harbor
from config import Setting
from src.gitlab_proxy import GitPipelineService
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

setting = Setting()


def _convert_testRunInfo_schema_to_db(testRunInfo: schema.TestRunInfo):
    return database.TestRunInfo(
        id=testRunInfo.id,
        pipelineAPI_id=testRunInfo.pipelineAPI_id,
        git_pipeline_id=testRunInfo.git_pipeline_id,
        create_time=testRunInfo.create_time,
        finish_time=testRunInfo.finish_time,
    )


def _convert_testRunInfo_db_to_schema(testRunInfo: database.TestRunInfo):
    return schema.TestRunInfo(
        id=testRunInfo.id,
        pipelineAPI_id=testRunInfo.pipelineAPI_id,
        git_pipeline_id=testRunInfo.git_pipeline_id,
        create_time=testRunInfo.create_time,
        finish_time=testRunInfo.finish_time,
        jobRuns=[],
        pipelineRuns=[],
    )


def get_testRunInfos(pipelineAPI_id: str):
    testRunInfo_repo = database.TestRunInfoRepository()
    db_testRunInfos = testRunInfo_repo.read_all_by_pipelineAPI_id(pipelineAPI_id)
    schema_testRunInfos = []
    for db_testRunInfo in db_testRunInfos:
        schema_testRunInfos.append(get_testRunInfo(db_testRunInfo.id))
    return schema_testRunInfos
    

def get_testRunInfo(testRunInfo_id: str):
    testRunInfo_repo = database.TestRunInfoRepository()
    db_testRunInfo = testRunInfo_repo.read_first(testRunInfo_id)
    schema_testRunInfo = _convert_testRunInfo_db_to_schema(db_testRunInfo)
    
    pipeline_service = GitPipelineService(db_testRunInfo.pipelineAPI.test_repository_id)
    jobs = pipeline_service.read_all_jobs(db_testRunInfo.git_pipeline_id)
    for job in jobs:
        job_obj = pipeline_service.read_job(job.id)
        schema_testRunInfo.jobRuns.append(job_obj)
    return schema_testRunInfo

def get_testRunInfo_job(testRunInfo_id: str, job_id: int):
    testRunInfo_repo = database.TestRunInfoRepository()
    db_testRunInfo = testRunInfo_repo.read_first(testRunInfo_id)

    pipeline_service = GitPipelineService(db_testRunInfo.pipelineAPI.test_repository_id)
    return pipeline_service.read_job(job_id)


def _convert_testPipelineRun_schema_to_db(testPipelineRun: schema.TestPipelineRun):
    return database.TestPipelineRun(
        id=testPipelineRun.id,
        testRunInfo_id=testPipelineRun.testRunInfo_id,
        git_pipeline_id=testPipelineRun.git_pipeline_id,
        create_time=testPipelineRun.create_time,
        finish_time=testPipelineRun.finish_time,
        callback_url=testPipelineRun.callback_url,
    )


def _convert_testPipelineRun_db_to_schema(testPipelineRun: database.TestPipelineRun):
    return schema.TestPipelineRun(
        id=testPipelineRun.id,
        testRunInfo_id=testPipelineRun.testRunInfo_id,
        git_pipeline_id=testPipelineRun.git_pipeline_id,
        create_time=testPipelineRun.create_time,
        finish_time=testPipelineRun.finish_time,
        callback_url=testPipelineRun.callback_url,
        jobRuns=[],
    )


def get_testPipelineRun(testPipelineRun_id: str):
    testPipelineRun_repo = database.TestPipelineRunRepository()
    db_testPipelineRun = testPipelineRun_repo.read_first(testPipelineRun_id)
    schema_testPipelineRun = _convert_testPipelineRun_db_to_schema(db_testPipelineRun)

    pipeline_service = GitPipelineService(db_testPipelineRun.testRunInfo.pipelineAPI.pipeline.repository_id)
    jobs = pipeline_service.read_all_jobs(db_testPipelineRun.git_pipeline_id)
    for job in jobs:
        job_obj = pipeline_service.read_job(job.id)
        schema_testPipelineRun.jobRuns.append(job_obj)
    return schema_testPipelineRun


def get_testPipelineRuns(testRunInfo_id: str):
    testPipelineRun_repo = database.TestPipelineRunRepository()
    db_testPipelineRuns = testPipelineRun_repo.read_all_by_testRunInfo_id(testRunInfo_id)
    schema_testPipelineRuns = []
    for db_testPipelineRun in db_testPipelineRuns:
        schema_testPipelineRuns.append(get_testPipelineRun(db_testPipelineRun.id))

    return schema_testPipelineRuns


def get_job(testPipelineRun_id: str, job_id: int):
    testPipelineRun_repo = database.TestPipelineRunRepository()
    testPipelineRun = testPipelineRun_repo.read_first(testPipelineRun_id)

    pipeline_service = GitPipelineService(testPipelineRun.testRunInfo.pipelineAPI.pipeline.repository_id)
    return pipeline_service.read_job(job_id)


def get_testPipelineRun_status(testPipelineRun_id: str):
    testPipelineRun_repo = database.TestPipelineRunRepository()
    testPipelineRun = testPipelineRun_repo.read_first(testPipelineRun_id)

    pipeline_service = GitPipelineService(testPipelineRun.testRunInfo.pipelineAPI.pipeline.repository_id)
    return pipeline_service.read_pipeline(testPipelineRun.git_pipeline_id).status


def store_mlflow_run_id(testPipelineRun_id: str, mlflow_run_id: str):
    testPipelineRun_repo = database.TestPipelineRunRepository()
    testPipelineRun = testPipelineRun_repo.read_first(testPipelineRun_id)
    testPipelineRun.mlflow_run_id = mlflow_run_id
    testPipelineRun_repo.update(testPipelineRun)