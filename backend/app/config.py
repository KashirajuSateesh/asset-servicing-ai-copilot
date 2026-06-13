from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Asset Servicing AI Copilot API"
    app_env: str = "development"

     # OpenAI
    openai_api_key: str | None = None

    # Azure SQL
    azure_sql_server: str | None = None
    azure_sql_database: str | None = None
    azure_sql_username: str | None = None
    azure_sql_password: str | None = None

    # Azure Blob Storage
    azure_storage_account_name: str | None = None
    azure_storage_connection_string: str | None = None

    # Azure AI Search
    azure_search_endpoint: str | None = None
    azure_search_key: str | None = None
    azure_search_index_name: str = "asset-policy-chunks"

    # Azure Cosmos DB 
    azure_cosmos_endpoint: str | None = None
    azure_cosmos_key: str | None = None
    azure_cosmos_database: str = "asset_copilot_memory"
    azure_cosmos_container: str = "agent_state"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()