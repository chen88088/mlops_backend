import time
import threading
import requests
import mlflow
from datetime import datetime as dt
from src.utils import datetime_to_string
from src.database import PipelineRunRepository, RunInfoRepository
from src.gitlab_proxy import GitPipelineService
from config import Setting

def callback(url):
    req = requests.get(url)
    print(req.status_code)

def tracking():
    pipelineRun_repo = PipelineRunRepository()
    runInfo_repo = RunInfoRepository()
    runs = pipelineRun_repo.read_all_running_pipelines()
    for run in runs:
        print(run.id)
        git_repository_id = run.runInfo.pipeline.repository_id
        git_service = GitPipelineService(git_repository_id)
        git_pipeline = git_service.read_pipeline(run.git_pipeline_id)
        if git_pipeline.finished_at == None:
            continue

        parse_datetime = dt.strptime(git_pipeline.finished_at.split('.')[0], '%Y-%m-%dT%H:%M:%S')
        run.finish_time = datetime_to_string(parse_datetime)
        pipelineRun_repo.update(run)
        runInfo = runInfo_repo.read_first(run.runInfo_id)
        runInfo.finish_time = datetime_to_string(parse_datetime)
        runInfo_repo.update(runInfo)
        if run.callback_url != None:
            threading.Thread(target=callback, args=(run.callback_url,))
        '''
        setting = Setting()
        client = mlflow.client.MlflowClient(tracking_uri=setting.mlflow_url)
        mlflow_runs = client.search_runs(experiment_ids=, order_by=["end_time DESC"], max_results=5)
        for mlflow_run in mlflow_runs:
        '''



#time.sleep(30)
while True:
    time.sleep(10)
    tracking()
