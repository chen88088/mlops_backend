# Database
- Adopt "sqlalchemy" as ORM for object-relational mapping.
- Implement the repository pattern by establishing "EntityRepository" in base.py, which provides the common CRUD function.
- Here data only includes that stored in PostgreSQL. If you need more complete data structures, please read the "schema" folder.

## File structure
### base.py
- Create the databases for backend and MLFlow
- Define "EntityRepository"