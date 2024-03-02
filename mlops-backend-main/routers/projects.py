from fastapi import APIRouter
from fastapi.responses import PlainTextResponse
from src import schema, database, project


router = APIRouter()

@router.post("/project/create", response_model=schema.Project, tags=["Projects"])
def create_project(project_name: str):
    return project.create_project(project_name)

@router.get("/project/list", response_model=list[schema.Project], tags=["Projects"])
def get_projects():
    project_repo = database.ProjectRepository()
    return project_repo.read_all()

@router.get("/project/{project_id}", response_model=schema.Project, tags=["Projects"])
def get_project(project_id: str):
    project_repo = database.ProjectRepository()
    return project_repo.read_first(project_id)

@router.delete("/project/{project_id}", tags=["Projects"])
def delete_project(project_id: str):
    project.delete_project(project_id)
    return PlainTextResponse("Success")