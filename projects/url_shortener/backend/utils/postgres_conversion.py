
def convert_postgres_sync_to_async(database_url:str):
    if database_url and database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://","postgresql+asyncpg://",1)
    return database_url