from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from src import schema, pipeline, database
from typing import Optional


router = APIRouter()

@router.get("/pipeline/{pipeline_id}/pipelineAPIs", response_model=list[schema.PipelineAPI], tags=["PipelineAPIs"])
def get_pipelineAPIs(pipeline_id: str, ):
    pipelineAPI_repo = database.PipelineAPIRepository()
    return pipelineAPI_repo.read_all_by_pipeline_id(pipeline_id)

@router.get("/pipeline/{pipeline_id}/default-pipelineAPI", response_model=schema.PipelineAPI, tags=["PipelineAPIs"])
def get_deault_pipelineAPI(pipeline_id: str):
    return pipeline.get_default_pipelineAPI(pipeline_id)

@router.get("/pipeline/{pipeline_id}/custom-pipelineAPIs", response_model=list[schema.PipelineAPI], tags=["PipelineAPIs"])
def get_custom_pipelineAPIs(pipeline_id: str):
    return pipeline.get_custom_pipelineAPIs(pipeline_id)

@router.post("/pipelineAPI/create", tags=["PipelineAPIs"])
def create_pipelineAPI(pipelineAPI: schema.PipelineAPI):
    pipelineAPI.id = schema.create_uuid()
    pipeline.create_pipelineAPI(pipelineAPI)
    return PlainTextResponse("Success")

@router.put("/pipelineAPI/update", tags=["PipelineAPIs"])
def update_pipelineAPI(pipelineAPI: schema.PipelineAPI):
    pipeline.update_pipelineAPI(pipelineAPI)
    return PlainTextResponse("Success")

@router.get("/pipelineAPI/{pipelineAPI_id}", response_model=schema.PipelineAPI, tags=["PipelineAPIs"])
def get_pipelineAPI(pipelineAPI_id: str):
    return pipeline.get_pipelineAPI(pipelineAPI_id)

@router.delete("/pipelineAPI/{pipelineAPI_id}", tags=["PipelineAPIs"])
def delete_pipelineAPI(pipelineAPI_id: str):
    pipelineAPI_repo = database.PipelineAPIRepository()
    pipelineAPI_repo.delete(pipelineAPI_id)
    return PlainTextResponse("Success")

@router.post("/pipelineAPI/{pipelineAPI_id}/run", tags=["PipelineAPIs"])
def run_pipelineAPI(pipelineAPI_id: str, options: Optional[dict] = None):
    variables = None
    callback_url = None
    if options != None:
        if 'variables' in options.keys():
            variables = options['variables']
        if 'callback_url' in options.keys():
            callback_url = options['callback_url']
    status_url = pipeline.run_pipelineAPI(pipelineAPI_id, False, variables, callback_url)
    return PlainTextResponse(status_url)

@router.post("/pipelineAPI/{pipelineAPI_id}/run/test", tags=["PipelineAPIs"])
def run_pipelineAPI_for_test(pipelineAPI_id: str, options: Optional[dict] = None):
    variables = None
    callback_url = None
    if options != None:
        if 'variables' in options.keys():
            variables = options['variables']
        if 'callback_url' in options.keys():
            callback_url = options['callback_url']
    status_url = pipeline.run_pipelineAPI(pipelineAPI_id, True, variables, callback_url)
    return PlainTextResponse(status_url)

@router.post("/pipelineAPI/{pipelineAPI_id}/start_test", tags=["PipelineAPIs"])
def test_pipelineAPI(pipelineAPI_id: str):
    pipeline.test_pipelineAPI(pipelineAPI_id)
    return PlainTextResponse("Success")