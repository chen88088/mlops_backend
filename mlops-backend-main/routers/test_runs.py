from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from src import schema, database, test_run


router = APIRouter()

@router.get("/pipelineAPI/{pipelineAPI_id}/testRunInfos", response_model=list[schema.TestRunInfo], tags=['TestRun'])
def get_testRunInfos(pipelineAPI_id: str):
    return test_run.get_testRunInfos(pipelineAPI_id)

@router.get("/testRunInfo/{testRunInfo_id}", response_model=schema.TestRunInfo, tags=['TestRun'])
def get_testRunInfo(testRunInfo_id: str):
    return test_run.get_testRunInfo(testRunInfo_id)

@router.get("/testRunInfo/{testRunInfo_id}/testPipelineRuns", response_model=list[schema.TestPipelineRun], tags=['TestRun'])
def get_testPipelineRuns(testRunInfo_id: str):
    return test_run.get_testPipelineRuns(testRunInfo_id)

@router.get("/testRunInfo/{testRunInfo_id}/job/{job_id}", response_model=dict, tags=['TestRun'])
def get_testRunInfo_job(testRunInfo_id: str, job_id: int):
    return test_run.get_testRunInfo_job(testRunInfo_id, job_id)

@router.get("/testPipelineRun/{testPipelineRun_id}", response_model=schema.TestPipelineRun, tags=['TestRun'])
def get_testPipelineRun(testPipelineRun_id: str):
    return test_run.get_testPipelineRun(testPipelineRun_id)

@router.get("/testPipelineRun/{testPipelineRun_id}/status", tags=['TestRun'])
def get_testPipelineRun_status(testPipelineRun_id: str):
    return PlainTextResponse(test_run.get_testPipelineRun_status(testPipelineRun_id))

@router.get("/testPipelineRun/{testPipelineRun_id}/job/{job_id}", response_model=dict, tags=['TestRun'])
def get_job(testPipelineRun_id: str, job_id: int):
    return test_run.get_job(testPipelineRun_id, job_id)

@router.put("/testPipelineRun/{testPipelineRun_id}/mlflow", tags=['TestRun'])
def store_mlflow_run(testPipelineRun_id: str, mlflow_run_id: str):
    test_run.store_mlflow_run_id(testPipelineRun_id, mlflow_run_id)
    return PlainTextResponse('Success')