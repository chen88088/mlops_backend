from config import Setting
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime as dt
from fastapi import HTTPException


class Harbor:
    def __init__(self):
        setting = Setting()
        self.harbor_url = setting.harbor_url
        self.username = setting.harbor_username
        self.password = setting.harbor_password
        self.login_url = f"{self.harbor_url}/login"
        self.api_url = f"{self.harbor_url}/api/v2.0"
        self.auth = HTTPBasicAuth(self.username, self.password)
    
    def get_projects(self):
        return requests.get(f"{self.api_url}/projects", auth=self.auth).json()
    
    def get_repos(self, project):
        return requests.get(f"{self.api_url}/projects/{project}/repositories", auth=self.auth).json()
    
    def get_artifacts(self, project, repo):
        return requests.get(f"{self.api_url}/projects/{project}/repositories/{repo}/artifacts", auth=self.auth).json()
    
    def get_image_list(self, project_name):
        base_name = self.harbor_url.split('//')[1]
        repos = self.get_repos(project_name)
        image_list = []
        for repo in repos:
            artifacts = self.get_artifacts(project_name, repo['name'].split('/')[1])

            latest_tag = ''
            latest_time = dt.min
            for artifact in artifacts:
                create_time = dt.strptime(artifact['extra_attrs']['created'].split('.')[0], '%Y-%m-%dT%H:%M:%S')
                if (create_time > latest_time):
                    latest_tag = artifact['tags'][0]['name']
            image_list.append(f"{base_name}/{repo['name']}:{latest_tag}")
        return image_list
    
    def create_project(self, project_name):
        data = {
            "project_name": project_name,
            "cve_allowlist": None,
            "registry_id": None,
            "public": True,
            "storage_limit": -1,
            "metadata": {
                "enable_content_trust": None,
                "enable_content_trust_cosign": None,
                "auto_scan": None,
                "severity": None,
                "retention_id": None,
                "prevent_vul": None,
                "public": "true",
                "reuse_sys_cve_allowlist": None
            }
        }
        res = requests.post(f"{self.api_url}/projects", json=data, auth=self.auth)
        if res.status_code != 201:
            raise HTTPException(
                status_code=404,
                detail=f'Create harbor project "{project_name}" fail.',
            )
    def delete_repo(self, project_name, repository_name):
        res = requests.delete(f"{self.api_url}/projects/{project_name}/repositories/{repository_name}", auth=self.auth)
        if res.status_code != 200:
            raise HTTPException(
                status_code=404,
                detail=f'Delete harbor repo "{repository_name}" fail.',
            )
        return res
    
    def delete_project(self, project_name):
        projects = self.get_projects()
        project_names = [project['name'] for project in projects]
        if project_name not in project_names:
            return
        repos = self.get_repos(project_name)
        for repo in repos:
            self.delete_repo(project_name, repo['name'].split('/')[1])
            
        res = requests.delete(f"{self.api_url}/projects/{project_name}", auth=self.auth)
        if res.status_code != 200:
            raise HTTPException(
                status_code=404,
                detail=f'Delete harbor project "{project_name}" fail.',
            )