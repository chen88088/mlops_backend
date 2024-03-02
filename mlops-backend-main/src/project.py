from src import gitlab_proxy as gitlab
from src import database, schema, harbor, minio_proxy
from config import Setting
from src.utils import datetime_to_string
from datetime import datetime
import logging
import mlflow

logger = logging.getLogger()
logger.setLevel(logging.INFO)

setting = Setting()


def _convert_project_schema_to_db(project: schema.Project):
    return database.Project(**project.dict())


def _convert_project_db_to_schema(project: database.Project):
    return schema.Project(**project.dict())


def _create_gitlab_pipeline(project_name: str, target: str):
    # Create ML pipeline for system
    ML_project_name = f"{target}-{project_name}"
    ML_project = gitlab.create_project(
        ML_project_name, setting.gitlab_system_group)
    pipeline_service = gitlab.GitPipelineService(ML_project.id)
    pipeline_service.create_pipeline_file()
    return ML_project.id

def _create_default_pipeline(project: database.Project):
    pipeline_repo = database.PipelineRepository()
    pipelineAPI_repo = database.PipelineAPIRepository()
    # create model training repo
    ML_project_id = _create_gitlab_pipeline(project.name, 'training')
    # create in sql
    pipeline = schema.Pipeline(
        project_id=project.id,
        repository_id=ML_project_id,
    )
    db_pipeline = database.Pipeline(**pipeline.dict())
    minio_proxy.create_bucket(db_pipeline.storage_bucket)
    minio_proxy.create_bucket(db_pipeline.data_version_bucket)
    minio_proxy.create_bucket(db_pipeline.test_storage_bucket)
    minio_proxy.create_bucket(db_pipeline.test_data_version_bucket)
    pipeline_repo.create_training(db_pipeline)

    # create model inference repo
    # create in gitlab
    ML_project_id = _create_gitlab_pipeline(project.name, 'inference')
    # create in sql
    pipeline = schema.Pipeline(
        project_id=project.id,
        repository_id=ML_project_id,
    )
    db_pipeline = database.Pipeline(**pipeline.dict())
    minio_proxy.create_bucket(db_pipeline.storage_bucket)
    minio_proxy.create_bucket(db_pipeline.data_version_bucket)
    minio_proxy.create_bucket(db_pipeline.test_storage_bucket)
    minio_proxy.create_bucket(db_pipeline.test_data_version_bucket)
    pipeline_repo.create_inference(db_pipeline)

def _delete_default_pipeline(project_id: str):
    pipeline_repo = database.PipelineRepository()
    pipelineJob_repo = database.PipelineJobRepository()
    pipelineAPI_repo = database.PipelineAPIRepository()
    runInfo_repo = database.RunInfoRepository()
    pipelineRun_repo = database.PipelineRunRepository()
    testRunInfo_repo = database.TestRunInfoRepository()
    testPipelineRun_repo = database.TestPipelineRunRepository()
    pipelines = pipeline_repo.read_all_by_project_id(project_id)
    # Delete pipelines
    for pipeline in pipelines:
        # Delete gitlab repo
        gitlab.delete_project(pipeline.repository_id)

        # Delete pipeline Job
        pipelineJobs = pipelineJob_repo.read_all_by_pipeline_id(pipeline.id)
        for pipelineJob in pipelineJobs:
            pipelineJob_repo.delete(pipelineJob.id)
        
        # Delete pipeline API
        pipelineAPIs = pipelineAPI_repo.read_all_by_pipeline_id(pipeline.id)
        for pipelineAPI in pipelineAPIs:
            # Delete testRunInfo repo
            testRunInfos = testRunInfo_repo.read_all_by_pipelineAPI_id(pipelineAPI.id)
            for testRunInfo in testRunInfos:
                # Delete testPipelineRun
                testPipelineRuns = testPipelineRun_repo.read_all_by_testRunInfo_id(testRunInfo.id)
                for testPipelineRun in testPipelineRuns:
                    testPipelineRun_repo.delete(testPipelineRun.id)
                testRunInfo_repo.delete(testRunInfo.id)
            
            # Delete pipelineRun
            pipelineRuns = pipelineRun_repo.read_all_by_pipelineAPI_id(pipelineAPI.id)
            for pipelineRun in pipelineRuns:
                pipelineRun_repo.delete(pipelineRun.id)
            
            # Delete pipelineAPI repo
            gitlab.delete_project(pipelineAPI.test_repository_id)
            pipelineAPI_repo.delete(pipelineAPI.id)

        # Delete runInfo repo
        runInfos = runInfo_repo.read_all_by_pipeline_id(pipeline.id)
        for runInfo in runInfos:
            # Delete pipelineRun
            pipelineRuns = pipelineRun_repo.read_all_by_runInfo_id(runInfo.id)
            for pipelineRun in pipelineRuns:
                pipelineRun_repo.delete(pipelineRun.id)
            runInfo_repo.delete(runInfo.id)
            
        minio_proxy.delete_bucket(pipeline.storage_bucket)
        minio_proxy.delete_bucket(pipeline.data_version_bucket)
        minio_proxy.delete_bucket(pipeline.test_storage_bucket)
        minio_proxy.delete_bucket(pipeline.test_data_version_bucket)
        pipeline_repo.delete(pipeline.id)

def _create_harbor_project(project: database.Project):
    harbor_serv = harbor.Harbor()
    harbor_serv.create_project(project.name)

def _delete_harbor_project(project_name: str):
    harbor_serv = harbor.Harbor()
    harbor_serv.delete_project(project_name)

def create_project(project_name: str):
    mlflow.set_tracking_uri(setting.mlflow_url)
    project = schema.Project(
        name=project_name,
        create_time=datetime_to_string(datetime.now()),
        mlflow_experiment_id=mlflow.create_experiment(schema.create_uuid()),
        test_mlflow_experiment_id=mlflow.create_experiment(schema.create_uuid())
    )
    project_repo = database.ProjectRepository()

    db_project = _convert_project_schema_to_db(project)
    db_project = project_repo.create(db_project)

    _create_default_pipeline(db_project)
    _create_harbor_project(db_project)
    
    return db_project

def delete_project(project_id: str):
    project_repo = database.ProjectRepository()
    del_project = project_repo.read_first(project_id)
    # Delete pipelines
    _delete_default_pipeline(project_id)
    _delete_harbor_project(del_project.name)
    # Delete project
    mlflow.set_tracking_uri(setting.mlflow_url)
    mlflow.delete_experiment(del_project.mlflow_experiment_id)
    mlflow.delete_experiment(del_project.test_mlflow_experiment_id)
    project_repo.delete(project_id)