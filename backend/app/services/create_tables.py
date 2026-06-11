from sqlalchemy import text

from app.services.azure_sql_service import get_engine
from app.services.sql_schema import TABLE_SCHEMAS


TABLE_DROP_ORDER = [
    "case_tickets",
    "corporate_actions",
    "settlement_exceptions",
    "reconciliation_breaks",
    "trade_status",
    "custody_accounts",
]


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


def reset_tables() -> dict:
    engine = get_engine()
    dropped_tables = []

    with engine.begin() as connection:
        for table_name in TABLE_DROP_ORDER:
            connection.execute(
                text(
                    f"""
                    IF OBJECT_ID('{table_name}', 'U') IS NOT NULL
                    DROP TABLE {table_name};
                    """
                )
            )
            dropped_tables.append(table_name)

    created_result = create_tables()

    return {
        "dropped_tables": dropped_tables,
        "created_result": created_result,
    }


if __name__ == "__main__":
    result = reset_tables()
    print(result)