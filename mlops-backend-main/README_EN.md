# MLOps-Backend
## Introduction
- This is the backend of MLOps system that provides REST API by framework FastAPI.
- This system integrates different tools, including that：
    - GitLab
    - MinIO
    - MLFlow
    - Harbor
    - PostgreSQL
## Folder structure
- routers
    - Manage different data by URL via FastAPI router
- src
    - Mainly source code
- .gitlab-ci.yml
    - Run the package work by GitLab CI/CD
- config.py
    - Read the environment variable setting
- Dockerfile
    - About how to package this project as container image
- main.py
    - The main program that define the setting about API server and some uncategorized APIs
- requirements.txt
    - The requirement for python library
- track_running_pipeline.py
    - Wait until the finish of running pipelines and store them back to PostgreSQL, but it contains some bugs.
- whitelist.txt
    - Define the allowable IPs that can connect to this API server.