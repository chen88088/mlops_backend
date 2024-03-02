from .base import create_gitlab_session
from config import Setting
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def create_project(project_name: str, namespace_name: str):
    with create_gitlab_session() as gl:
        try:
            namespace = gl.namespaces.get(namespace_name)
            project = gl.projects.create(
                {'name': project_name, 'namespace_id': namespace.id})
            logger.debug(f'Create new project "{project_name}" in GitLab success.')
            return project
        except Exception as e:
            logger.error(f'Create new project "{project_name}" in GitLab fail.\n{e}')

def get_project(id: int):
    with create_gitlab_session() as gl:
        try:
            project = gl.projects.get(id)
            logger.debug(f'Get project "id={id}" in GitLab success.')
            return project
        except Exception as e:
            logger.error(f'Get project "id={id}" in GitLab fail.\n{e}')

def delete_project(id: int):
    with create_gitlab_session() as gl:
        try:
            project = gl.projects.delete(id)
            logger.debug(f'Delete project "id={id}" in GitLab success.')
            return project
        except Exception as e:
            logger.error(f'Delete project "id={id}" in GitLab fail.\n{e}')

def get_project_url(id: int):
    setting = Setting()
    prefix = setting.gitlab_url
    suffixes = get_project(id).attributes["web_url"].split('/')[3:]
    suffix_url = ''
    for piece in suffixes:
        suffix_url = suffix_url + piece + '/'
    return f"{prefix}{suffix_url}"