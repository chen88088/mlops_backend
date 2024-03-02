from minio import Minio
from config import Setting
from io import BytesIO
import zipfile

def create_client():
    setting = Setting()
    return Minio(
        endpoint=setting.minio_url,
        access_key=setting.minio_access_key,
        secret_key=setting.minio_secret_key,
        secure=False
    )

def create_bucket(bucket_name):
    client = create_client()
    client.make_bucket(bucket_name)

def delete_bucket(bucket_name):
    client = create_client()
    objs = client.list_objects(bucket_name, recursive=True)
    for obj in objs:
        client.remove_object(bucket_name, obj.object_name)
    client.remove_bucket(bucket_name)

def read_objects(bucket_name, folder_name=''):
    client = create_client()
    objs = client.list_objects(bucket_name, prefix=folder_name, recursive=False)
    res = []
    for obj in objs:
        res.append({
            'object_name': obj.object_name,
            'size': obj.size,
            'last_modified': obj.last_modified,
            'is_dir': obj.is_dir,
        })
    return res

def delete_object(bucket_name, object_name):
    client = create_client()
    client.remove_object(bucket_name, object_name)

def delete_folder(bucket_name, folder_name):
    client = create_client()
    objs = client.list_objects(bucket_name, prefix=folder_name, recursive=True)
    for obj in objs:
        client.remove_object(bucket_name, obj.object_name)

def create_upload_link(bucket_name, object_name):
    client = create_client()
    url = client.presigned_put_object(bucket_name, object_name)
    return url

def create_download_link(bucket_name, object_name):
    client = create_client()
    filename = object_name.split('/')[-1]
    url = client.presigned_get_object(bucket_name, object_name, response_headers={'response-content-disposition': f'attachment; name={filename}'})
    return url

def download_folder(bucket_name, folder_name):
    mem_zip = BytesIO()
    short_folder_name = folder_name.split('/')[-2]
    zip_name = f"{short_folder_name}.zip"
    with zipfile.ZipFile(mem_zip, mode="w",compression=zipfile.ZIP_DEFLATED) as zf:
        client = create_client()
        objs = client.list_objects(bucket_name, prefix=folder_name, recursive=True)
        for obj in objs:
            if obj.is_dir:
                continue
            filename_in_zip = obj.object_name[len(folder_name):]
            try:
                res = client.get_object(bucket_name, obj.object_name)
                binaries = b''
                for data in res.stream(1024):
                    binaries += data                    
                zf.writestr(filename_in_zip, binaries)
            finally:
                res.close()
                res.release_conn()

    return mem_zip.getvalue(), zip_name
