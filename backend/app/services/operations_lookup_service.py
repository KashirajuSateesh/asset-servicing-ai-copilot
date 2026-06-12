from app.services.operations_data_service import (
    get_case_by_id,
    get_exception_by_id,
    get_reconciliation_break_by_id,
    get_trade_by_id,
)


def detect_record_type(record_id: str) -> str | None:
    """
    Detects what type of operational record the user is asking about.

    Why this is useful:
    Agents and MCP tools should not need to manually decide which SQL function
    to call every time. This helper looks at the ID prefix and routes the lookup.

    Supported examples:
    - TRD-0000001  -> trade
    - EXC-000001   -> settlement_exception
    - BRK-0000001  -> reconciliation_break
    - CASE-0000001 -> case_ticket
    """

    record_id_upper = record_id.upper().strip()

    if record_id_upper.startswith("TRD-"):
        return "trade"

    if record_id_upper.startswith("EXC-"):
        return "settlement_exception"

    if record_id_upper.startswith("BRK-"):
        return "reconciliation_break"

    if record_id_upper.startswith("CASE-"):
        return "case_ticket"

    return None


def lookup_operational_record(record_id: str) -> dict:
    """
    Looks up an operational record from Azure SQL based on its ID.

    This is a unified lookup layer for agents.

    Instead of the agent calling separate functions for trade, exception,
    break, or case, it can call this one function with the record ID.
    """

    record_type = detect_record_type(record_id)

    if not record_type:
        return {
            "record_id": record_id,
            "record_type": None,
            "found": False,
            "message": "Unsupported record ID format.",
            "data": None,
        }

    if record_type == "trade":
        data = get_trade_by_id(record_id)

    elif record_type == "settlement_exception":
        data = get_exception_by_id(record_id)

    elif record_type == "reconciliation_break":
        data = get_reconciliation_break_by_id(record_id)

    elif record_type == "case_ticket":
        data = get_case_by_id(record_id)

    else:
        data = None

    return {
        "record_id": record_id,
        "record_type": record_type,
        "found": data is not None,
        "data": data,
    }