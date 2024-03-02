from fastapi import APIRouter
from fastapi.responses import PlainTextResponse, Response
from src import minio_proxy
from typing import Optional


router = APIRouter()


@router.get("/storage/{bucket_name}/list", tags=['Storage'])
def list_objects(bucket_name: str, prefix: Optional[str] = '/'):
    return minio_proxy.read_objects(bucket_name, prefix)


@router.delete("/storage/{bucket_name}/object", tags=['Storage'])
def delete_object(bucket_name: str, object_name: str):
    return minio_proxy.delete_object(bucket_name, object_name)


@router.delete("/storage/{bucket_name}/objects", tags=['Storage'])
def delete_folder(bucket_name: str, object_name: str):
    return minio_proxy.delete_folder(bucket_name, object_name)


@router.get("/storage/{bucket_name}/object/upload", tags=['Storage'])
def upload_object(bucket_name: str, object_name: str):
    url = minio_proxy.create_upload_link(bucket_name, object_name)
    return PlainTextResponse(url)


@router.get("/storage/{bucket_name}/object/download", tags=['Storage'])
def download_object(bucket_name: str, object_name: str):
    url = minio_proxy.create_download_link(bucket_name, object_name)
    return PlainTextResponse(url)


@router.get("/storage/{bucket_name}/objects/download", tags=['Storage'])
def download_folder(bucket_name: str, object_name: str):
    file_bytes, file_name = minio_proxy.download_folder(
        bucket_name, object_name)
    return Response(file_bytes, media_type='application/zip',
                             headers={
                                 'Content-Disposition': f'attachment; filename="{file_name}"'
                             })
