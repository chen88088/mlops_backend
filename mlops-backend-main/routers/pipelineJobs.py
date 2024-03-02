from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from src import schema, pipeline


router = APIRouter()

@router.get("/pipeline/{pipeline_id}/pipelineJobs", response_model=list[schema.PipelineJob], tags=["PipelineJobs"])
def get_pipelineJobs(pipeline_id: str):
    return pipeline.get_pipelineJobs(pipeline_id)

@router.post("/pipelineJob/create", tags=["PipelineJobs"])
def create_pipelineJob(pipelineJob: schema.PipelineJob):
    pipelineJob.id = schema.create_uuid()
    pipeline.create_pipelineJob(pipelineJob)
    return PlainTextResponse("Success")

@router.get("/pipelineJob/{pipelineJob_id}", response_model=schema.PipelineJob, tags=["PipelineJobs"])
def get_pipelineJob(pipelineJob_id: str):
    return pipeline.get_pipelineJob(pipelineJob_id)

@router.put("/pipelineJob/update", tags=["PipelineJobs"])
def update_pipelineJob(pipelineJob: schema.PipelineJob):
    pipeline.update_pipelineJob(pipelineJob)
    return PlainTextResponse("Success")

@router.delete("/pipelineJob/{pipelineJob_id}", tags=["PipelineJobs"])
def delete_pipelineJob(pipelineJob_id: str):
    pipeline.delete_pipelineJob(pipelineJob_id)
    return PlainTextResponse("Success")