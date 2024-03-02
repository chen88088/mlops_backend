# Database
- 採用 sqlalchemy 作為 orm 進行物件關聯對映
- 參考 repository pattern 在 base.py 中建立 EntityRepository 提供通用的 CRUD
- 此處資料庫資訊僅包含存於 PostgreSQL 的資料，需要更完整角度的資料結構請參考 schema 資料夾

## File structure
### base.py
- 建立 backend 與 MLFlow 使用的資料庫
- 定義 EntityRepository