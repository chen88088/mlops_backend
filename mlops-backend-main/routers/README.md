# Sequence Diagrams

## Projects

### Create project
<details>
<summary>Diagram</summary>

```mermaid
sequenceDiagram
    User->>Backend: New project name
    Backend->>MLFlow: Create product and test experiments in MLFlow
    Backend->>Backend: Create "Project" object
    Backend->>PostgreSQL: Store object
    Backend->>GitLab: Create training and inference pipelines repository in GitLab
    Backend->>MinIO: Create 4 buckets for each ML pipeline
    Backend->>Harbor: Create a harbor project to store container images for this project.
```
</details>

### Delete project
<details>
<summary>Diagram</summary>

```mermaid
sequenceDiagram
    User->>Backend: Project id
    Backend->>PostgreSQL: Delete related "pipeline" objects
    Backend->>GitLab: Delete ML pipeline repositories
    Backend->>MinIO: Delete 4 buckets for each related ML pipeline
    Backend->>Harbor: Delete the related harbor project
    Backend->>MLFlow: Delete product and test experiments in MLFlow
    Backend->>PostgreSQL: Delete "Project" object
```
</details>

## Pipelines

### Get a pipeline by Id
<details>
<summary>Diagram</summary>

```mermaid
sequenceDiagram
    User->>Backend: Pipeline id
    Backend->>PostgreSQL: Get "Pipeline" object
    Backend-->>User: Return the information
```
</details>

### Get a pipeline by project id and type
<details>
<summary>Diagram</summary>

```mermaid
sequenceDiagram
    User->>Backend: Project id and specifc route
    Backend->>PostgreSQL: Get "Pipeline" object
    Backend-->>User: Return the information
```
</details>

## PipelineJobs

### Create pipelineJob
<details>
<summary>Diagram</summary>

```mermaid
sequenceDiagram
    User->>Backend: PipelineJob object
    Backend->>Backend: Give object "id" and "order"
    Backend->>GitLab: Update .gitlab-ci.yml
    Backend->>PostgreSQL: Store new job object
    alt First job for this pipeline
        Backend->>GitLab: Create test code repo for E2E API
        Backend->>PostgreSQL: Create the default E2E API
    else Not first job for this pipeline
        Backend->>PostgreSQL: Update the default E2E API
    end
```
</details>

### Get pipelineJob
<details>
<summary>Diagram</summary>

```mermaid
sequenceDiagram
    User->>Backend: PipelineJob id
    Backend->>PostgreSQL: Get job object
    Backend->>GitLab: Read the related job from .gitlab-ci.yml
    Backend-->>User: Return PipelineJob object
```
</details>

### Update pipelineJob
<details>
<summary>Diagram</summary>

```mermaid
sequenceDiagram
    User->>Backend: Updated PipelineJob object
    Backend->>GitLab: Update .gitlab-ci.yml
    Backend->>PostgreSQL: Update job object
```
</details>

### Delete pipelineJob
<details>
<summary>Diagram</summary>

```mermaid
sequenceDiagram
    User->>Backend: PipelineJob id
    Backend->>GitLab: Reorder other jobs in the same pipeline
    Backend->>GitLab: Update .gitlab-ci.yml
    Backend->>PostgreSQL: Remove job object
    alt 0 job in the same pipeline
        Backend->>GitLab: Delete test code repo for E2E API
        Backend->>PostgreSQL: Delete the default E2E API
    else 1 or more jobs in the same pipeline
        Backend->>PostgreSQL: Update the default E2E API
    end
```
</details>

## PipelieAPIs

### Create pipelineAPI
<details>
<summary>Diagram</summary>

```mermaid
sequenceDiagram
    User->>Backend: PipelineAPI object
    Backend->>Backend: Give object "id"
    Backend->>GitLab: Create test code repo for this API
    Backend->>PostgreSQL: Store new API object
```
</details>

### Get pipelineAPI
<details>
<summary>Diagram</summary>

```mermaid
sequenceDiagram
    User->>Backend: PipelineAPI id
    Backend->>Backend: Give the system environment variables
    Backend->>PostgreSQL: Get the job object that run in this API
    Backend->>GitLab: Give the custom environment variables
    Backend-->>User: Return PipelineAPI object
```
</details>

### Update pipelineAPI
<details>
<summary>Diagram</summary>

```mermaid
sequenceDiagram
    User->>Backend: Updated PipelineAPI object
    Backend->>PostgreSQL: Update object
```
</details>

### Delete pipelineAPI
<details>
<summary>Diagram</summary>

```mermaid
sequenceDiagram
    User->>Backend: PipelineAPI id
    Backend->>PostgreSQL: Delete PipelineAPI object
```
</details>

### Run pipelineAPI
<details>
<summary>Diagram</summary>

```mermaid
sequenceDiagram
    User->>Backend: PipelineAPI id, variable values, and purpose by route
    Backend->>Backend: Add the variable values from "flow_control", system-defined ones, and user-defined ones.
    Backend->>GitLab: Run CI/CD pipeline in ML pipeline repo
    alt route for production
        alt RunInfo object doesn't exist
            Backend->>PostgreSQL: Create new RunInfo object
        end
        Backend->>PostgreSQL: Create new PipelineRun object
    else route for testing
        Backend->>PostgreSQL: UpCreateate the TestPipelineRun object
    end
```
</details>

### Test pipelineAPI
<details>
<summary>Diagram</summary>

```mermaid
sequenceDiagram
    User->>Backend: PipelineAPI id
    Backend->>Backend: Add the system-defined variable values
    Backend->>GitLab: Run CI/CD pipeline in test code repo
    Backend->>PostgreSQL: Create new TestRunInfo object
```
</details>

## Runs

### Get RunInfo
<details>
<summary>Diagram</summary>

```mermaid
sequenceDiagram
    User->>Backend: RunInfo id
    Backend->>PostgreSQL: Get object 
    Backend-->>User: Return RunInfo object
```
</details>

### Get PipelineRun
<details>
<summary>Diagram</summary>

```mermaid
sequenceDiagram
    User->>Backend: PipelineRun id
    Backend->>PostgreSQL: Get object
    Backend->>GitLab: Get execution logs 
    Backend-->>User: Return PipelineRun object
```
</details>

### Get running status of PipelineRun
<details>
<summary>Diagram</summary>

```mermaid
sequenceDiagram
    User->>Backend: PipelineRun id
    Backend->>PostgreSQL: Get object
    Backend->>GitLab: Get job objects  
    Backend-->>User: Return status text
```
</details>

### Get job information of PipelineRun
<details>
<summary>Diagram</summary>

```mermaid
sequenceDiagram
    User->>Backend: PipelineRun id and job id
    Backend->>PostgreSQL: Get object 
    Backend->>GitLab: Get specific job object
    Backend-->>User: Return job object
```
</details>

## TestRuns

### Get TestRunInfo
<details>
<summary>Diagram</summary>

```mermaid
sequenceDiagram
    User->>Backend: TestRunInfo id
    Backend->>PostgreSQL: Get object 
    Backend->>GitLab: Get CI/CD pipeline execution result 
    Backend-->>User: Return TestRunInfo object
```
</details>

### Get TestPipelineRun
<details>
<summary>Diagram</summary>

```mermaid
sequenceDiagram
    User->>Backend: TestPipelineRun id
    Backend->>PostgreSQL: Get object
    Backend->>GitLab: Get execution job objects 
    Backend-->>User: Return TestPipelineRun object
```
</details>

### Get running status of TestPipelineRun
<details>
<summary>Diagram</summary>

```mermaid
sequenceDiagram
    User->>Backend: TestPipelineRun id
    Backend->>PostgreSQL: Get object
    Backend->>GitLab: Get execution status 
    Backend-->>User: Return status text
```
</details>

### Get job information of TestPipelineRun
<details>
<summary>Diagram</summary>

```mermaid
sequenceDiagram
    User->>Backend: TestPipelineRun id and job id
    Backend->>PostgreSQL: Get object 
    Backend->>GitLab: Get specific job object
    Backend-->>User: Return job object
```
</details>

## Storage

### Upload file object
<details>
<summary>Diagram</summary>

```mermaid
sequenceDiagram
    User->>Backend: Bucket name and object name
    Backend->>MinIO: Get object upload url 
    Backend-->>User: Return upload url
```
</details>

### Get file objects
<details>
<summary>Diagram</summary>

```mermaid
sequenceDiagram
    User->>Backend: Bucket name and folder name
    Backend->>MinIO: Get object list 
    Backend-->>User: Return file and folder list
```
</details>

### Download file object
<details>
<summary>Diagram</summary>

```mermaid
sequenceDiagram
    User->>Backend: Bucket name and object name
    Backend->>MinIO: Get object download url 
    Backend-->>User: Return download url
```
</details>

### Delete file object
<details>
<summary>Diagram</summary>

```mermaid
sequenceDiagram
    User->>Backend: Bucket name and object name
    Backend->>MinIO: Remove the object
```
</details>

### Download folder
<details>
<summary>Diagram</summary>

```mermaid
sequenceDiagram
    User->>Backend: Bucket name and folder name
    Backend->>MinIO: Get each object in the folder
    Backend->>Backend: Package each object into a zip file
    Backend-->>User: Return zip file
```
</details>

### Delete folder
<details>
<summary>Diagram</summary>

```mermaid
sequenceDiagram
    User->>Backend: Bucket name and folder name
    Backend->>MinIO: Get each object in the folder
    Backend->>MinIO: Delete each object in the folder
```
</details>