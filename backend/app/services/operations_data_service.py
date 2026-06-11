from sqlalchemy import text

from app.services.azure_sql_service import get_engine


def rows_to_dicts(rows) -> list[dict]:
    return [dict(row._mapping) for row in rows]


def get_dashboard_summary() -> dict:
    engine = get_engine()

    queries = {
        "custody_accounts": "SELECT COUNT(*) AS count FROM custody_accounts",
        "trades": "SELECT COUNT(*) AS count FROM trade_status",
        "settlement_exceptions": "SELECT COUNT(*) AS count FROM settlement_exceptions",
        "reconciliation_breaks": "SELECT COUNT(*) AS count FROM reconciliation_breaks",
        "case_tickets": "SELECT COUNT(*) AS count FROM case_tickets",
        "corporate_actions": "SELECT COUNT(*) AS count FROM corporate_actions",
    }

    summary = {}

    with engine.connect() as connection:
        for key, query in queries.items():
            result = connection.execute(text(query))
            row = result.fetchone()
            summary[key] = row.count if row else 0

    return summary


def get_trade_by_id(trade_id: str) -> dict | None:
    engine = get_engine()

    query = text(
        """
        SELECT TOP 1 *
        FROM trade_status
        WHERE trade_id = :trade_id
        """
    )

    with engine.connect() as connection:
        result = connection.execute(query, {"trade_id": trade_id})
        row = result.fetchone()

    return dict(row._mapping) if row else None


def get_exception_by_id(exception_id: str) -> dict | None:
    engine = get_engine()

    query = text(
        """
        SELECT TOP 1 *
        FROM settlement_exceptions
        WHERE exception_id = :exception_id
        """
    )

    with engine.connect() as connection:
        result = connection.execute(query, {"exception_id": exception_id})
        row = result.fetchone()

    return dict(row._mapping) if row else None


def get_reconciliation_break_by_id(break_id: str) -> dict | None:
    engine = get_engine()

    query = text(
        """
        SELECT TOP 1 *
        FROM reconciliation_breaks
        WHERE break_id = :break_id
        """
    )

    with engine.connect() as connection:
        result = connection.execute(query, {"break_id": break_id})
        row = result.fetchone()

    return dict(row._mapping) if row else None


def get_case_by_id(case_id: str) -> dict | None:
    engine = get_engine()

    query = text(
        """
        SELECT TOP 1 *
        FROM case_tickets
        WHERE case_id = :case_id
        """
    )

    with engine.connect() as connection:
        result = connection.execute(query, {"case_id": case_id})
        row = result.fetchone()

    return dict(row._mapping) if row else None