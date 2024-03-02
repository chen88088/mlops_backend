from .base import create_gitlab_session
from .project import get_project
import logging
import yaml
from fastapi import HTTPException

logger = logging.getLogger()
logger.setLevel(logging.INFO)

pipelineTemplate = {
    'workflow': {'rules': [{'if': '$CI_PIPELINE_SOURCE == \"api\"'}]},
    'variables': {
        'PROJECT_ID': '',
        'RUN_ID': '',
        'MLFLOW_URL': '',
        'MLFLOW_EXP_ID': '',
        'S3_URL': '',
        'S3_ACCESS_KEY': '',
        'S3_SECRET_KEY': '',
        'S3_DATA_BUCKET': '',
        'S3_VERSION_BUCKET': '',
    },
}
class GitPipelineService():
    def __init__(self, project_id: int):
        self.project_id = project_id
        self.project = get_project(project_id)
    
    def create_pipeline_file(self):
        try:
            data = {
                'branch': 'main',
                'commit_message': 'Initial ML pipeline',
                'actions': [
                    {
                        'action': 'create',
                        'file_path': '.gitlab-ci.yml',
                        'content': yaml.dump(pipelineTemplate),
                    },
                ]
            }
            commit = self.project.commits.create(data)
            logger.debug(f'Create new pipeline "id={self.project_id}" in GitLab success.')
        except Exception as e:
            logger.error(f'Create new pipeline "id={self.project_id}" in GitLab fail.\n{e}')
            raise HTTPException(
                status_code=404,
                detail=f'Create GitLab pipeline fail.',
            )
    
    def read_pipeline_file(self):
        try:
            pipeline_file = self.project.files.get(file_path='.gitlab-ci.yml', ref='main')
            pipeline_text = pipeline_file.decode()
            self.pipeline = yaml.safe_load(pipeline_text)
        except Exception as e:
            logger.error(f'Read pipeline "id={self.project_id}" in GitLab fail.\n{e}')
            raise HTTPException(
                status_code=404,
                detail=f'Read GitLab pipeline fail.',
            )

    def commit_pipeline_file(self):
        try:
            data = {
                'branch': 'main',
                'commit_message': 'Update ML pipeline',
                'actions': [
                    {
                        'action': 'update',
                        'file_path': '.gitlab-ci.yml',
                        'content': self.pipeline_to_str(),
                    },
                ]
            }
            commit = self.project.commits.create(data)
            logger.debug(f'Commit pipeline in GitLab success.')
        except Exception as e:
            logger.error(f'Update pipeline "id={self.project_id}" in GitLab fail.\n{e}')
            raise HTTPException(
                status_code=404,
                detail=f'Update pipeline pipeline fail.',
            )
    
    def pipeline_to_str(self):
        return yaml.dump(self.pipeline)

    def add_job(self, key: str, value: dict):
        self.pipeline[key] = value
    
    def remove_job(self, key: str):
        del self.pipeline[key]
    
    def find_job_by_name(self, name: str):
        if name in self.pipeline.keys():
            return name, self.pipeline[name]
        return None, None
    
    def add_stage(self, order: int):
        if 'stages' not in self.pipeline.keys():
            self.pipeline['stages'] = []
        self.pipeline['stages'].append(f'stage{order}')
    
    def remove_stage(self, order: int):
        self.pipeline['stages'].remove(f'stage{order}')

    def run_pipeline(self, variables):
        var_array = []
        for key in variables:
            var_array.append({
                'key': key,
                'value': variables[key]
            })
        data = {
            'ref': 'main',
            'variables': var_array
        }
        new_pipeline = self.project.pipelines.create(data)
        return new_pipeline

    def read_pipeline(self, pipeline_id):
        return self.project.pipelines.get(pipeline_id)

    def read_all_jobs(self, pipeline_id):
        return self.read_pipeline(pipeline_id).jobs.list()

    def read_job(self, job_id):
        job = self.project.jobs.get(job_id)
        job_obj = job.asdict()
        log = job.trace()
        filter_rn_lineslines = log.split(b'\r\n')
        filter_n_lines = []
        for line in filter_rn_lineslines:
            filter_n_lines += line.split(b'\n')

        log_lines = []
        for line in filter_n_lines:
            while line.find(b'\r') != -1:
                line = line[line.find(b'\r')+1:]
            log_lines.append(line)
            
        job_obj['logs'] = log_lines
        return job_obj