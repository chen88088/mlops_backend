from fastapi import APIRouter, UploadFile
from fastapi.responses import PlainTextResponse, Response
from src import mlflow_proxy
from typing import Optional


router = APIRouter()
'''
@router.get("/mlflow/??", tags=["PipelineAPIs"])
def get_artifacts(pipeline_id: str, ):
    file_bytes, file_name = mlflow_proxy.get_artifacts()
    return Response(file_bytes, media_type='application/zip',
                             headers={
                                 'Content-Disposition': f'attachment; filename="{file_name}"'
                             })'''