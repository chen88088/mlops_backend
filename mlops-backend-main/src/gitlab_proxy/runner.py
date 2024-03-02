from .base import create_gitlab_session
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def get_runners_tag():
    with create_gitlab_session() as gl:
        try:
            runners = gl.runners_all.list()
            runners_tag = []
            for runner in runners:
                runner = gl.runners.get(runner.id)
                runners_tag.append(runner.tag_list[0])
            logger.debug(f'Get runner tags in GitLab success.')
            return runners_tag
        except Exception as e:
            logger.error(f'Get runner tags in GitLab fail.\n{e}')