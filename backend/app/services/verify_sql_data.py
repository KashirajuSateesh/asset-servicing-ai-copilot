from sqlalchemy import text

from app.services.azure_sql_service import get_engine


TABLES = [
    "custody_accounts",
    "trade_status",
    "settlement_exceptions",
    "reconciliation_breaks",
    "case_tickets",
    "corporate_actions",
]


def verify_table_counts() -> list[dict]:
    engine = get_engine()
    results = []

    with engine.connect() as connection:
        for table_name in TABLES:
            result = connection.execute(
                text(f"SELECT COUNT(*) AS row_count FROM {table_name}")
            )
            row = result.fetchone()

            results.append(
                {
                    "table": table_name,
                    "row_count": row.row_count if row else 0,
                }
            )

    return results


if __name__ == "__main__":
    counts = verify_table_counts()

    for item in counts:
        print(item)