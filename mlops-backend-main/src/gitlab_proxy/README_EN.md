# GitLab proxy
- Develop the needed function based on package "python-gitlab"

## File structure
### base.py
- Define the connection between backend and GitLab
    - Decorate the connection function by Context Manager, other functions can use the syntactic sugar "with" to close the connection automatically.

### project.py
- The creation, getter, and deletion of the code repository in GitLab.

### pipeline.py
- Manage the ML pipeline in GitLab, including that updating pipeline configurations, executing pipelines, and getting the execution record.

### runner.py
- Get the information of registered runners in GitLab.