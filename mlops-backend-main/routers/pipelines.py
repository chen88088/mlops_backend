from fastapi import APIRouter
from src import schema, database


router = APIRouter()

@router.get("/project/{project_id}/pipelines", response_model=list[schema.Pipeline], tags=["Pipelines"])
def get_pipelines(project_id: str):
    pipeline_repo = database.PipelineRepository()
    return pipeline_repo.read_all_by_project_id(project_id)

@router.get("/project/{project_id}/training-pipeline", response_model=schema.Pipeline, tags=["Pipelines"])
def get_training_pipeline(project_id: str):
    pipeline_repo = database.PipelineRepository()
    return pipeline_repo.read_training(project_id)

@router.get("/project/{project_id}/inference-pipeline", response_model=schema.Pipeline, tags=["Pipelines"])
def get_inference_pipeline(project_id: str):
    pipeline_repo = database.PipelineRepository()
    return pipeline_repo.read_inference(project_id)

@router.get("/pipeline/{pipeline_id}", response_model=schema.Pipeline, tags=["Pipelines"])
def get_pipeline(pipeline_id: str):
    pipeline_repo = database.PipelineRepository()
    return pipeline_repo.read_first(pipeline_id)