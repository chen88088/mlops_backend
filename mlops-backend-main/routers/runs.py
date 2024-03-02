from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from src import schema, database, run


router = APIRouter()

@router.get("/pipeline/{pipeline_id}/runInfos", response_model=list[schema.RunInfo], tags=['Run'])
def get_runInfos(pipeline_id: str):
    return run.get_runInfos(pipeline_id)

@router.get("/runInfo/{runInfo_id}", response_model=schema.RunInfo, tags=['Run'])
def get_runInfo(runInfo_id: str):
    return run.get_runInfo(runInfo_id)

@router.get("/runInfo/{runInfo_id}/pipelineRuns", response_model=list[schema.PipelineRun], tags=['Run'])
def get_pipelineRuns(runInfo_id: str):
    return run.get_pipelineRuns(runInfo_id)

@router.get("/pipelineRun/{pipelineRun_id}", response_model=schema.PipelineRun, tags=['Run'])
def get_pipelineRun(pipelineRun_id: str):
    return run.get_pipelineRun(pipelineRun_id)

@router.get("/pipelineRun/{pipelineRun_id}/status", tags=['Run'])
def get_pipelineRun_status(pipelineRun_id: str):
    return PlainTextResponse(run.get_pipelineRun_status(pipelineRun_id))

@router.get("/pipelineRun/{pipelineRun_id}/job/{job_id}", response_model=dict, tags=['Run'])
def get_job(pipelineRun_id: str, job_id: int):
    return run.get_job(pipelineRun_id, job_id)

@router.put("/pipelineRun/{pipelineRun_id}/mlflow", tags=['Run'])
def store_mlflow_run(pipelineRun_id: str, mlflow_run_id: str):
    run.store_mlflow_run_id(pipelineRun_id, mlflow_run_id)
    return PlainTextResponse('Success')