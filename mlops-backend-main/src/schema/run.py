from pydantic import Field
from .base import create_uuid, OrmModel
from typing import Optional
from gitlab.v4.objects.pipelines import ProjectPipelineJob
from .pipeline import PipelineAPI


class PipelineRun(OrmModel):
    id: str = Field(default_factory=create_uuid)
    runInfo_id: str
    pipelineAPI_id: str
    git_pipeline_id: int
    mlflow_run_id: Optional[str]
    create_time: str
    finish_time: Optional[str]
    callback_url: Optional[str]
    pipelineAPI: PipelineAPI
    jobRuns: Optional[list]


class RunInfo(OrmModel):
    id: str = Field(default_factory=create_uuid)
    pipeline_id: str
    create_time: str
    finish_time: Optional[str]
    pipelineRuns: list[PipelineRun]