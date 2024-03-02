from src import gitlab_proxy as gitlab
from src import database, schema, harbor
from config import Setting
from src.gitlab_proxy import GitPipelineService
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

setting = Setting()


def _convert_runInfo_schema_to_db(runInfo: schema.RunInfo):
    return database.RunInfo(
        id=runInfo.id,
        pipeline_id=runInfo.pipeline_id,
        create_time=runInfo.create_time,
        finish_time=runInfo.finish_time,
    )


def _convert_runInfo_db_to_schema(runInfo: database.RunInfo):
    return schema.RunInfo(
        id=runInfo.id,
        pipeline_id=runInfo.pipeline_id,
        create_time=runInfo.create_time,
        finish_time=runInfo.finish_time,
        pipelineRuns=[],
    )


def get_runInfos(pipeline_id: str):
    runInfo_repo = database.RunInfoRepository()
    db_runInfos = runInfo_repo.read_all_by_pipeline_id(pipeline_id)
    schema_runInfos = []
    for db_runInfo in db_runInfos:
        schema_runInfos.append(get_runInfo(db_runInfo.id))
    return schema_runInfos
    

def get_runInfo(runInfo_id: str):
    runInfo_repo = database.RunInfoRepository()
    db_runInfo = runInfo_repo.read_first(runInfo_id)
    schema_runInfo = _convert_runInfo_db_to_schema(db_runInfo)
    return schema_runInfo


def _convert_pipelineRun_schema_to_db(pipelineRun: schema.PipelineRun):
    return database.PipelineRun(
        id=pipelineRun.id,
        runInfo_id=pipelineRun.runInfo_id,
        pipelineAPI_id=pipelineRun.pipelineAPI_id,
        git_pipeline_id=pipelineRun.git_pipeline_id,
        create_time=pipelineRun.create_time,
        finish_time=pipelineRun.finish_time,
        callback_url=None,
    )


def _convert_pipelineRun_db_to_schema(pipelineRun: database.PipelineRun):
    return schema.PipelineRun(
        id=pipelineRun.id,
        runInfo_id=pipelineRun.runInfo_id,
        pipelineAPI_id=pipelineRun.pipelineAPI_id,
        git_pipeline_id=pipelineRun.git_pipeline_id,
        create_time=pipelineRun.create_time,
        finish_time=pipelineRun.finish_time,
        callback_url=None,
        pipelineAPI=pipelineRun.pipelineAPI,
        jobRuns=[],
    )


def get_pipelineRun(pipelineRun_id: str):
    pipelineRun_repo = database.PipelineRunRepository()
    db_pipelineRun = pipelineRun_repo.read_first(pipelineRun_id)
    schema_pipelineRun = _convert_pipelineRun_db_to_schema(db_pipelineRun)

    pipeline_service = GitPipelineService(db_pipelineRun.pipelineAPI.pipeline.repository_id)
    jobs = pipeline_service.read_all_jobs(db_pipelineRun.git_pipeline_id)
    for job in jobs:
        job_obj = pipeline_service.read_job(job.id)
        schema_pipelineRun.jobRuns.append(job_obj)
    return schema_pipelineRun    


def get_pipelineRuns(runInfo_id: str):
    pipelineRun_repo = database.PipelineRunRepository()
    db_pipelineRuns = pipelineRun_repo.read_all_by_runInfo_id(runInfo_id)
    schema_pipelineRuns = []
    for db_pipelineRun in db_pipelineRuns:
        schema_pipelineRuns.append(get_pipelineRun(db_pipelineRun.id))

    return schema_pipelineRuns


def get_job(pipelineRun_id: str, job_id: int):
    pipelineRun_repo = database.PipelineRunRepository()
    pipelineRun = pipelineRun_repo.read_first(pipelineRun_id)

    pipeline_service = GitPipelineService(pipelineRun.pipelineAPI.pipeline.repository_id)
    return pipeline_service.read_job(job_id)


def get_pipelineRun_status(pipelineRun_id: str):
    pipelineRun_repo = database.PipelineRunRepository()
    db_pipelineRun = pipelineRun_repo.read_first(pipelineRun_id)

    pipeline_service = GitPipelineService(db_pipelineRun.pipelineAPI.pipeline.repository_id)
    return pipeline_service.read_pipeline(db_pipelineRun.git_pipeline_id).status


def store_mlflow_run_id(pipelineRun_id: str, mlflow_run_id: str):
    pipelineRun_repo = database.PipelineRunRepository()
    pipelineRun = pipelineRun_repo.read_first(pipelineRun_id)
    pipelineRun.mlflow_run_id = mlflow_run_id
    pipelineRun_repo.update(pipelineRun)