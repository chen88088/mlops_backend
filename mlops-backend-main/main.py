from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from src import schema, database, project, pipeline, gitlab_proxy, harbor, minio_proxy
from routers import projects, pipelines, pipelineJobs, pipelineAPIs, runs, storage, test_runs


app = FastAPI()
app.include_router(projects.router)
app.include_router(pipelines.router)
app.include_router(pipelineJobs.router)
app.include_router(pipelineAPIs.router)
app.include_router(runs.router)
app.include_router(storage.router)
app.include_router(test_runs.router)
# read CORS white list
origins = []
with open('whitelist.txt', 'r') as f:
    for line in f:
        line_strip = line.strip()
        origins.append(str(line_strip))

app.add_middleware(
    CORSMiddleware,
    # 允許發出跨域請求的來源列表
    allow_origins=origins,
    # 表示跨域請求應該支持 cookie
    allow_credentials=True,
    # 跨域請求應允許的 HTTP 方法列表, ['*']允許所有標準方法
    allow_methods=["*"],
    # 跨域請求應支持的 HTTP 請求標頭列表, ['*']允許所有標頭
    allow_headers=["*"],
)

database.base.Base.metadata.create_all(bind=database.engine)

@app.get("/git/runners-tag", response_model=list[str])
def get_git_runners_tag():
    return gitlab_proxy.get_runners_tag()

@app.get("/git/project-name-with-namespace/{id}")
def get_git_project_name_with_namespace(id: int):
    return PlainTextResponse(gitlab_proxy.get_project_url(id))

@app.get("/harbor/{project_id}/list", response_model=list[str])
def get_image_list(project_id: str):
    project_repo = database.ProjectRepository()
    project = project_repo.read_first(project_id)
    harbor_serv = harbor.Harbor()
    return harbor_serv.get_image_list(project.name)

@app.get("/callbacktest")
def test():
    print(1)
    return PlainTextResponse('Success')