# MLOps-Backend
## 介紹
- 這是 MLOps 系統的後端，採用 FastAPI 來提供 REST API，此系統背後整合了不同的工具，包含：
    - GitLab
    - MinIO
    - MLFlow
    - Harbor
    - PostgreSQL
## 資料夾結構
- routers
    - 利用 FastAPI router 將不同資料的使用路徑進行區分管理
- src
    - 此後端主要的原始碼位置
- .gitlab-ci.yml
    - 可以搭配 GitLab 進行自動打包
- config.py
    - 用來讀取外部設定的環境變數
- Dockerfile
    - 將本專案進行打包成容器的設定檔
- main.py
    - 本專案主程式，設定 API 伺服器，並包含一部份難分類的 API
- requirements.txt
    - 本專案的 python 函式庫需求
- track_running_pipeline.py
    - 用來追蹤管道運行結果，並且結束狀態寫回資料庫，目前仍有 bug
- whitelist.txt
    - 用來設定 FastAPI 運行時可存取的白名單