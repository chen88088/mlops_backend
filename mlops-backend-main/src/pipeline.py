from src import database, schema
from config import Setting
from src.gitlab_proxy import GitPipelineService
from src import gitlab_proxy as gitlab
from fastapi import Depends
import logging
from datetime import datetime as dt
from src.utils import datetime_to_string
from typing import Optional

logger = logging.getLogger()
logger.setLevel(logging.INFO)

setting = Setting()


# Pipeline Job
def _convert_pipelineJob_schema_to_config(job: schema.PipelineJob):
    key = job.name
    value = {
        'stage': f'stage{job.order}',
        'tags': [job.runner_tag],
        'script': job.instructions,
        'variables': dict(zip([x['name'] for x in job.variables], [x['value'] for x in job.variables])),
        'rules': [{'if': f'$run{job.order} == \"1\"'}]
    }
    if job.os == "Linux":
        value['image'] = job.image
    if len(value['script']) == 0:
        del value['script']
    if len(value['variables']) == 0:
        del value['variables']

    return key, value


def _convert_pipelineJob_config_to_schema(job: schema.PipelineJob, git_pipeline: GitPipelineService):
    key, value = git_pipeline.find_job_by_name(job.name)

    if 'variables' in value.keys():
        for v_key in value['variables'].keys():
            job.variables.append(
                {'name': v_key, 'value': value['variables'][v_key]})
    if 'script' in value.keys():
        job.instructions = value['script']

    return job


def _convert_pipelinejob_schema_to_db(job: schema.PipelineJob):
    return database.PipelineJob(
        id=job.id,
        pipeline_id=job.pipeline_id,
        order=job.order,
        name=job.name,
        os=job.os,
        image=job.image,
        runner_tag=job.runner_tag
    )


def _convert_pipelinejob_db_to_schema(job: database.PipelineJob):
    return schema.PipelineJob(
        id=job.id,
        pipeline_id=job.pipeline_id,
        order=job.order,
        name=job.name,
        os=job.os,
        image=job.image,
        runner_tag=job.runner_tag,
        variables=[],
        instructions=[],
    )


def _create_flow_control_variable(pipeline_id: str):
    pipelineJob_repo = database.PipelineJobRepository()
    all_jobs = pipelineJob_repo.read_all_by_pipeline_id(pipeline_id)
    flow_control = {}
    for job in all_jobs:
        flow_control[f'run{job.order}'] = '1'
    return flow_control


def create_pipelineJob(job: schema.PipelineJob):
    pipeline_repo = database.PipelineRepository()
    pipelineJob_repo = database.PipelineJobRepository()

    current_jobs = pipelineJob_repo.read_all_by_pipeline_id(job.pipeline_id)
    job.order = len(current_jobs) + 1
    pipeline = pipeline_repo.read_first(job.pipeline_id)

    # update job to gitlab
    pipeline_service = GitPipelineService(pipeline.repository_id)
    pipeline_service.read_pipeline_file()
    key, value = _convert_pipelineJob_schema_to_config(job)
    pipeline_service.add_job(key, value)
    pipeline_service.add_stage(job.order)
    pipeline_service.commit_pipeline_file()

    # update job to sql
    db_job = _convert_pipelinejob_schema_to_db(job)
    db_job = pipelineJob_repo.create(db_job)
    # update pipeline API
    if db_job.order == 1:
        _create_default_pipelineAPI(pipeline)
    else:
        _update_default_pipelineAPI(pipeline)


def get_pipelineJob(job_id: str):
    pipeline_repo = database.PipelineRepository()
    pipelineJob_repo = database.PipelineJobRepository()

    db_job = pipelineJob_repo.read_first(job_id)
    job = _convert_pipelinejob_db_to_schema(db_job)
    pipeline = pipeline_repo.read_first(job.pipeline_id)

    # Read job from gitlab
    pipeline_service = GitPipelineService(pipeline.repository_id)
    pipeline_service.read_pipeline_file()
    job = _convert_pipelineJob_config_to_schema(job, pipeline_service)
    return job


def get_pipelineJobs(pipeline_id: str):
    pipelineJob_repo = database.PipelineJobRepository()
    db_jobs = pipelineJob_repo.read_all_by_pipeline_id(pipeline_id)
    jobs = [get_pipelineJob(db_job.id) for db_job in db_jobs]
    return jobs


def update_pipelineJob(job: schema.PipelineJob):
    pipeline_repo = database.PipelineRepository()
    pipelineJob_repo = database.PipelineJobRepository()
    pipeline = pipeline_repo.read_first(job.pipeline_id)
    original_job = pipelineJob_repo.read_first(job.id)

    # update job to gitlab
    pipeline_service = GitPipelineService(pipeline.repository_id)
    pipeline_service.read_pipeline_file()
    key, _ = pipeline_service.find_job_by_name(original_job.name)
    if key is not None:
        pipeline_service.remove_job(key)
    key, value = _convert_pipelineJob_schema_to_config(job)
    pipeline_service.add_job(key, value)
    pipeline_service.commit_pipeline_file()

    # update job to sql
    db_job = _convert_pipelinejob_schema_to_db(job)
    pipelineJob_repo.update(db_job)


# Delete the specific job, and others after it go foward.
# For example: If I need to delete the 3rd job
# Job's order: 1 -> 2 -> 3 -> 4 -> 5
# Remove the 3rd job
# Job's order: 1 -> 2 -> 4 -> 5
# All jobs after the 3rd job move forward 1 rank.
# Job's order: 1 -> 2 -> 3 -> 4
def delete_pipelineJob(id: str):
    pipeline_repo = database.PipelineRepository()
    pipelineJob_repo = database.PipelineJobRepository()
    delete_job = pipelineJob_repo.read_first(id)
    pipeline_id = delete_job.pipeline_id
    all_jobs = pipelineJob_repo.read_all_by_pipeline_id(pipeline_id)
    after_delete_jobs = [
        job for job in all_jobs if job.order > delete_job.order]
    pipeline = pipeline_repo.read_first(pipeline_id)
    pipeline_service = GitPipelineService(pipeline.repository_id)
    pipeline_service.read_pipeline_file()

    # remove last stage
    if len(after_delete_jobs) == 0:
        pipeline_service.remove_stage(delete_job.order)
    else:
        max_order = max([x.order for x in after_delete_jobs])
        pipeline_service.remove_stage(max_order)

        # Move forward 1 rank
        for job in after_delete_jobs:
            schema_job = get_pipelineJob(job.id)
            schema_job.order -= 1
            job = _convert_pipelinejob_schema_to_db(schema_job)
            update_result = pipelineJob_repo.update(job)
            key, _ = pipeline_service.find_job_by_name(job.name)
            if key is not None:
                pipeline_service.remove_job(key)
            key, value = _convert_pipelineJob_schema_to_config(schema_job)
            pipeline_service.add_job(key, value)

    # Remove the specific job
    pipeline_service.remove_job(delete_job.name)
    pipeline_service.commit_pipeline_file()

    pipelineJob_repo.delete(delete_job.id)

    # update pipeline API
    all_jobs = pipelineJob_repo.read_all_by_pipeline_id(pipeline_id)
    if len(all_jobs) > 0:
        _update_default_pipelineAPI(pipeline)
    else:
        _delete_default_pipelineAPI(pipeline)


# Pipeline API
def convert_pipelineAPI_schema_to_db(api: schema.PipelineAPI):
    return database.PipelineAPI(
        id=api.id,
        pipeline_id=api.pipeline_id,
        name=api.name,
        type=api.type,
        flow_control=api.flow_control,
        test_repository_id=api.test_repository_id,
    )


def convert_pipelineAPI_db_to_schema(api: database.PipelineAPI):
    return schema.PipelineAPI(
        id=api.id,
        pipeline_id=api.pipeline_id,
        name=api.name,
        type=api.type,
        flow_control=api.flow_control,
        test_repository_id=api.test_repository_id,
        test_repository_url=None if api.test_repository_id == None else gitlab.get_project_url(api.test_repository_id),
        jobs=[],
        api_url=f"{setting.system_url}/pipelineAPI/{api.id}/run",
        test_api_url=f"{setting.system_url}/pipelineAPI/{api.id}/run/test",
        system_variables=[
            'PROJECT_ID', 'RUN_ID', 'MLFLOW_URL',
            'MLFLOW_EXP_ID', 'S3_URL', 'S3_ACCESS_KEY',
            'S3_SECRET_KEY', 'S3_DATA_BUCKET', 'S3_VERSION_BUCKET',
        ],
        user_variables=[],
    )


def _create_pipeline_variables(pipeline: database.pipeline, test: bool, custom_variables: dict = {}):
    if custom_variables == None:
        custom_variables = {}
    custom_variables['PROJECT_ID'] = pipeline.project_id
    if 'RUN_ID' not in custom_variables:
        custom_variables['RUN_ID'] = schema.create_uuid()

    setting = Setting()
    custom_variables['MLFLOW_URL'] = setting.mlflow_url
    custom_variables['S3_URL'] = f"http://{setting.minio_url}"
    custom_variables['S3_ACCESS_KEY'] = setting.minio_access_key
    custom_variables['S3_SECRET_KEY'] = setting.minio_secret_key
    custom_variables['TESTING'] = test

    # Give storage resource for different purpose pipeline
    project_repo = database.ProjectRepository()
    project = project_repo.read_first(pipeline.project_id)
    if test:
        custom_variables['MLFLOW_EXP_ID'] = project.test_mlflow_experiment_id
        custom_variables['S3_DATA_BUCKET'] = pipeline.test_storage_bucket
        custom_variables['S3_VERSION_BUCKET'] = pipeline.test_data_version_bucket
    else:
        custom_variables['MLFLOW_EXP_ID'] = project.mlflow_experiment_id
        custom_variables['S3_DATA_BUCKET'] = pipeline.storage_bucket
        custom_variables['S3_VERSION_BUCKET'] = pipeline.data_version_bucket
    return custom_variables


def _create_default_pipelineAPI(pipeline: schema.Pipeline):
    pipelineAPI_repo = database.PipelineAPIRepository()
    api = schema.PipelineAPI(
        name="Default API",
        pipeline_id=pipeline.id,
        flow_control=_create_flow_control_variable(pipeline.id),
    )
    api.test_repository_id = _create_pipelineAPI_test_pipeline(api)
    db_api = convert_pipelineAPI_schema_to_db(api)
    pipelineAPI_repo.create_default(db_api)


def _update_default_pipelineAPI(pipeline: schema.Pipeline):
    pipelineAPI_repo = database.PipelineAPIRepository()
    db_api = pipelineAPI_repo.read_default(pipeline.id)
    db_api.flow_control = _create_flow_control_variable(pipeline.id)
    pipelineAPI_repo.update(db_api)


def _delete_default_pipelineAPI(pipeline: schema.Pipeline):
    pipelineAPI_repo = database.PipelineAPIRepository()
    db_api = pipelineAPI_repo.read_default(pipeline.id)
    pipelineAPI_repo.delete(db_api.id)


def _create_pipelineAPI_test_pipeline(api: schema.PipelineAPI):
    # Create test pipeline for user
    pipeline_repo = database.PipelineRepository()
    pipeline = pipeline_repo.read_first(api.pipeline_id)
    test_project_name = f"TestPipeline-{pipeline.project.name}-{api.name}"
    test_project = gitlab.create_project(test_project_name, setting.gitlab_NCU_group)
    return test_project.id


def get_pipelineAPI(api_id: str):
    pipelineAPI_repo = database.PipelineAPIRepository()
    db_api = pipelineAPI_repo.read_first(api_id)
    api = convert_pipelineAPI_db_to_schema(db_api)

    pipelineJobs = get_pipelineJobs(api.pipeline_id)
    user_variable_set = set()
    for pipelineJob in pipelineJobs:
        if api.flow_control[f"run{pipelineJob.order}"] == "1":
            api.jobs.append(pipelineJob)
            for user_variable in pipelineJob.variables:
                user_variable_set.add(user_variable['name'])

    api.user_variables = list(user_variable_set)

    api.jobs.sort(key=lambda s: s.order)
    return api


def get_default_pipelineAPI(pipeline_id: str):
    pipelineAPI_repo = database.PipelineAPIRepository()
    db_api = pipelineAPI_repo.read_default(pipeline_id)
    return get_pipelineAPI(db_api.id)


def get_custom_pipelineAPIs(pipeline_id: str):
    pipelineAPI_repo = database.PipelineAPIRepository()
    db_apis = pipelineAPI_repo.read_customs(pipeline_id)
    schema_apis = []
    for db_api in db_apis:
        schema_apis.append(get_pipelineAPI(db_api.id))
    return schema_apis


def create_pipelineAPI(api: schema.PipelineAPI):
    api.test_repository_id = _create_pipelineAPI_test_pipeline(api)
    db_api = convert_pipelineAPI_schema_to_db(api)
    pipelineAPI_repo = database.PipelineAPIRepository()
    db_api = pipelineAPI_repo.create_custom(db_api)
    return db_api


def update_pipelineAPI(api: schema.PipelineAPI):
    db_api = convert_pipelineAPI_schema_to_db(api)
    pipelineAPI_repo = database.PipelineAPIRepository()
    db_api = pipelineAPI_repo.update(db_api)
    return db_api


def run_pipelineAPI(api_id: str, test: bool, custom_variables: Optional[dict] = None, callback_url: Optional[str] = None):
    pipelineAPI_repo = database.PipelineAPIRepository()
    pipeline_repo = database.PipelineRepository()

    api = pipelineAPI_repo.read_first(api_id)
    pipeline = pipeline_repo.read_first(api.pipeline_id)

    variables = api.flow_control
    pipeline_variables = _create_pipeline_variables(
        pipeline, test, custom_variables)
    for key in pipeline_variables:
        variables[key] = pipeline_variables[key]

    pipeline_service = GitPipelineService(pipeline.repository_id)
    git_pipeline_info = pipeline_service.run_pipeline(variables)
    
    if test:
        testRunInfo_repo = database.TestRunInfoRepository()
        db_testRun = testRunInfo_repo.read_first(variables['RUN_ID'])

        testPipelineRun_repo = database.TestPipelineRunRepository()
        db_testPipelineRun = database.TestPipelineRun(
            id=schema.create_uuid(),
            testRunInfo_id=db_testRun.id,
            git_pipeline_id=git_pipeline_info.id,
            mlflow_run_id="",
            create_time=datetime_to_string(dt.strptime(
                git_pipeline_info.created_at.split('.')[0], '%Y-%m-%dT%H:%M:%S')),
            finish_time=None,
            callback_url=callback_url
        )
        testPipelineRun_repo.create(db_testPipelineRun)
        return f"/testPipelineRun/{db_testPipelineRun.id}/status"
    else:
        runInfo_repo = database.RunInfoRepository()
        db_run = runInfo_repo.read_first(variables['RUN_ID'])
        if db_run == None:
            db_run = database.RunInfo(
                id=variables['RUN_ID'],
                pipeline_id=pipeline.id,
                create_time=datetime_to_string(dt.now())
            )
            db_run = runInfo_repo.create(db_run)

        pipelineRun_repo = database.PipelineRunRepository()
        db_pipelineRun = database.PipelineRun(
            id=schema.create_uuid(),
            runInfo_id=db_run.id,
            pipelineAPI_id=api_id,
            git_pipeline_id=git_pipeline_info.id,
            mlflow_run_id="",
            create_time=datetime_to_string(dt.strptime(
                git_pipeline_info.created_at.split('.')[0], '%Y-%m-%dT%H:%M:%S')),
            finish_time=None,
            callback_url=callback_url
        )
        pipelineRun_repo.create(db_pipelineRun)
        return f"/pipelineRun/{db_pipelineRun.id}/status"


def test_pipelineAPI(api_id: str):
    pipelineAPI_repo = database.PipelineAPIRepository()
    pipeline_repo = database.PipelineRepository()

    api = pipelineAPI_repo.read_first(api_id)
    pipeline = pipeline_repo.read_first(api.pipeline_id)

    variables = {}
    pipeline_variables = _create_pipeline_variables(pipeline, True, None)
    for key in pipeline_variables:
        variables[key] = pipeline_variables[key]

    pipeline_service = GitPipelineService(api.test_repository_id)
    git_pipeline_info = pipeline_service.run_pipeline(variables)

    testRunInfo_repo = database.TestRunInfoRepository()
    db_testRun = database.TestRunInfo(
        id=variables['RUN_ID'],
        pipelineAPI_id=api_id,
        git_pipeline_id=git_pipeline_info.id,
        create_time=datetime_to_string(dt.now())
    )
    db_testRun = testRunInfo_repo.create(db_testRun)