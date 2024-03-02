from pydantic import Field
from typing import Optional
from .base import create_uuid, OrmModel


class PipelineJob(OrmModel):
    id: str = Field(default_factory=create_uuid)
    pipeline_id: str
    order: int
    name: str
    os: str
    image: str
    runner_tag: str
    variables: list[dict]
    instructions: list[str]


class PipelineAPI(OrmModel):
    id: str = Field(default_factory=create_uuid)
    pipeline_id: str
    name: str
    type: Optional[str]
    flow_control: dict
    test_repository_id: Optional[int]
    test_repository_url: Optional[str]
    jobs: Optional[list[PipelineJob]]
    api_url: Optional[str]
    test_api_url: Optional[str]
    system_variables: Optional[list[str]]
    user_variables: Optional[list[str]]
    

class Pipeline(OrmModel):
    id: str = Field(default_factory=create_uuid)
    project_id: str
    type: Optional[str]
    repository_id: int
    storage_bucket: str = Field(default_factory=create_uuid)
    data_version_bucket: str = Field(default_factory=create_uuid)
    test_storage_bucket: str = Field(default_factory=create_uuid)
    test_data_version_bucket: str = Field(default_factory=create_uuid)