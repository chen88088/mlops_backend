# GitLab proxy
- 基於 python-gitlab 將原有進行開發建立需要的功能

## File structure
### base.py
- 定義與 GitLab 的連線
    - 透過 Context Manager 可以使用 with 語法糖自行關閉連線

### project.py
- 新增、取得、刪除 GitLab 中的 project

### pipeline.py
- 管理在 GitLab 中的 ML pipeline，包含更新管道設定、執行管道、取得執行紀錄

### runner.py
- 取得 GitLab 中已經註冊的 runner 資訊