from pydantic import Field
from .base import create_uuid, OrmModel
from typing import Optional
from gitlab.v4.objects.pipelines import ProjectPipelineJob
from .pipeline import PipelineAPI

class TestPipelineRun(OrmModel):
    id: str = Field(default_factory=create_uuid)
    testRunInfo_id: str
    git_pipeline_id: int
    mlflow_run_id: Optional[str]
    create_time: str
    finish_time: Optional[str]
    callback_url: Optional[str]
    jobRuns: Optional[list]

class TestRunInfo(OrmModel):
    id: str = Field(default_factory=create_uuid)
    pipelineAPI_id: str
    git_pipeline_id: int
    create_time: str
    finish_time: Optional[str]
    jobRuns: Optional[list]
    pipelineRuns: list[TestPipelineRun]