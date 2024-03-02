from contextlib import contextmanager
from config import Setting
import gitlab
import logging
from fastapi import HTTPException

logger = logging.getLogger()
logger.setLevel(logging.INFO)

@contextmanager
def create_gitlab_session():
    setting = Setting()
    try:
        git_session = gitlab.Gitlab(
            url=setting.gitlab_url,
            private_token=setting.gitlab_token
        )
        logger.debug("Create GitLab session success")
        yield git_session
    except Exception as e:
        logger.error(f"Create GitLab session fail\n{e}")
        raise HTTPException(
            status_code=404,
            detail=f'Create GitLab session fail.',
        )
    finally:
        git_session.session.close()