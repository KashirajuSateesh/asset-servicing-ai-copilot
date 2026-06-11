from sqlalchemy import text

from app.services.azure_sql_service import get_engine
from app.services.sql_schema import TABLE_SCHEMAS


def table_exists(table_name: str) -> bool:
    engine = get_engine()

    query = text(
        """
        SELECT COUNT(*) AS table_count
        FROM INFORMATION_SCHEMA.TABLES
        WHERE TABLE_NAME = :table_name
        """
    )

    with engine.connect() as connection:
        result = connection.execute(query, {"table_name": table_name})
        row = result.fetchone()

    return row.table_count > 0 if row else False


def create_tables() -> dict:
    engine = get_engine()
    created_tables = []
    skipped_tables = []

    with engine.begin() as connection:
        for table_name, create_sql in TABLE_SCHEMAS.items():
            if table_exists(table_name):
                skipped_tables.append(table_name)
                continue

            connection.execute(text(create_sql))
            created_tables.append(table_name)

    return {
        "created_tables": created_tables,
        "skipped_existing_tables": skipped_tables,
        "total_created": len(created_tables),
        "total_skipped": len(skipped_tables),
    }


if __name__ == "__main__":
    result = create_tables()
    print(result)