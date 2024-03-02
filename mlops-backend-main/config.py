import os
from pydantic import BaseSettings
from requests.auth import HTTPBasicAuth


class Setting(BaseSettings):
    db_url: str = os.environ["DB_URL"]
    db_user: str = os.environ["DB_USER"]
    db_password: str = os.environ["DB_PASSWORD"]
    gitlab_url: str = os.environ["GITLAB_URL"]
    gitlab_token: str = os.environ["GITLAB_TOKEN"]
    gitlab_system_group: str = "mlops-system"
    gitlab_NCU_group: str = "ncu-issl"
    harbor_url: str = os.environ["HARBOR_URL"]
    harbor_username: str = os.environ["HARBOR_USERNAME"]
    harbor_password: str = os.environ["HARBOR_PASSWORD"]
    minio_url: str = os.environ["MINIO_URL"]
    minio_access_key: str = os.environ["MINIO_ACCESS_KEY"]
    minio_secret_key: str = os.environ["MINIO_SECRET_KEY"]
    mlflow_url: str = os.environ["MLFLOW_URL"]
    system_url: str = os.environ["SYSTEM_URL"]
