from urllib.parse import quote_plus

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from app.config import settings


def get_sqlalchemy_url() -> str:
    if not all(
        [
            settings.azure_sql_server,
            settings.azure_sql_database,
            settings.azure_sql_username,
            settings.azure_sql_password,
        ]
    ):
        raise ValueError("Azure SQL configuration is missing.")

    driver = "ODBC Driver 18 for SQL Server"

    odbc_connection = (
        f"DRIVER={{{driver}}};"
        f"SERVER={settings.azure_sql_server};"
        f"DATABASE={settings.azure_sql_database};"
        f"UID={settings.azure_sql_username};"
        f"PWD={settings.azure_sql_password};"
        "Encrypt=yes;"
        "TrustServerCertificate=no;"
        "Connection Timeout=30;"
    )

    return f"mssql+pyodbc:///?odbc_connect={quote_plus(odbc_connection)}"


def get_engine() -> Engine:
    return create_engine(
        get_sqlalchemy_url(),
        pool_pre_ping=True,
        pool_recycle=1800,
    )


def test_sql_connection() -> dict:
    engine = get_engine()

    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1 AS test_value"))
        row = result.fetchone()

    return {
        "connected": True,
        "test_value": row.test_value if row else None,
    }