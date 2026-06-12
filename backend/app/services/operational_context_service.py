from app.services.operations_lookup_service import lookup_operational_record


def build_operational_context(record_id: str) -> dict:
    """
    Builds a clean operational context object for a given record ID.

    Why this is useful:
    Agents should not directly work with raw SQL records every time.
    This service converts the lookup result into a consistent context format
    that can be passed to an LLM, an MCP tool, or an orchestrator.

    Current version:
    - Looks up one operational record.
    - Returns record type, raw data, and a short context summary.

    Future version:
    - Add related account lookup.
    - Add related trade lookup.
    - Add related policy/RAG guidance.
    - Save workflow state into Cosmos DB.
    """

    # Step 1: Look up the operational record from Azure SQL.
    lookup_result = lookup_operational_record(record_id)

    # Step 2: If no record is found, return a safe response.
    if not lookup_result.get("found"):
        return {
            "record_id": record_id,
            "record_type": lookup_result.get("record_type"),
            "found": False,
            "context_summary": "No supported operational record was found for this ID.",
            "record_data": None,
        }

    record_type = lookup_result["record_type"]
    record_data = lookup_result["data"]

    # Step 3: Build a simple business-friendly summary based on record type.
    if record_type == "trade":
        context_summary = (
            f"Trade {record_data.get('trade_id')} is a "
            f"{record_data.get('side')} trade for account {record_data.get('account_id')} "
            f"with status {record_data.get('trade_status')} and settlement date "
            f"{record_data.get('settlement_date')}."
        )

    elif record_type == "settlement_exception":
        context_summary = (
            f"Settlement exception {record_data.get('exception_id')} is linked to trade "
            f"{record_data.get('trade_id')} for account {record_data.get('account_id')}. "
            f"The severity is {record_data.get('severity')} and current status is "
            f"{record_data.get('exception_status')}."
        )

    elif record_type == "reconciliation_break":
        context_summary = (
            f"Reconciliation break {record_data.get('break_id')} is for account "
            f"{record_data.get('account_id')}. The break type is "
            f"{record_data.get('break_type')} with variance amount "
            f"{record_data.get('variance_amount')} {record_data.get('currency')} "
            f"and status {record_data.get('break_status')}."
        )

    elif record_type == "case_ticket":
        context_summary = (
            f"Case {record_data.get('case_id')} is assigned to "
            f"{record_data.get('assigned_team')} with priority "
            f"{record_data.get('priority')} and SLA status "
            f"{record_data.get('sla_status')}."
        )

    else:
        context_summary = "Operational record found, but no summary template is available."

    # Step 4: Return a consistent context object.
    return {
        "record_id": record_id,
        "record_type": record_type,
        "found": True,
        "context_summary": context_summary,
        "record_data": record_data,
    }