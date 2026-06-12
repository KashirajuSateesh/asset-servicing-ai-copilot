from app.services.operational_context_service import build_operational_context
from app.services.rag_answer_service import generate_rag_answer


def build_policy_question_from_context(context: dict) -> str:
    """
    Builds a policy/RAG question from operational context.

    Why this is needed:
    The user may only provide a record ID like EXC-000001.
    The system needs to transform that record into a policy question that
    can be searched against SOP and policy documents.

    Example:
    EXC-000001 is a settlement exception with exposure and SLA details.
    We turn that into:
    "What policy guidance applies to a settlement exception with this severity,
    status, exposure, and SLA condition?"
    """

    record_type = context.get("record_type")
    record_data = context.get("record_data") or {}

    if record_type == "settlement_exception":
        return (
            "What policy guidance applies to a settlement exception with "
            f"reason '{record_data.get('exception_reason')}', "
            f"severity '{record_data.get('severity')}', "
            f"status '{record_data.get('exception_status')}', "
            f"estimated exposure USD {record_data.get('estimated_exposure_usd')}, "
            f"and SLA due date {record_data.get('sla_due_date')}?"
        )

    if record_type == "reconciliation_break":
        return (
            "What policy guidance applies to a reconciliation break with "
            f"break type '{record_data.get('break_type')}', "
            f"variance amount {record_data.get('variance_amount')} "
            f"{record_data.get('currency')}, "
            f"aging days {record_data.get('aging_days')}, "
            f"status '{record_data.get('break_status')}', "
            f"and root cause '{record_data.get('root_cause')}'?"
        )

    if record_type == "trade":
        return (
            "What policy guidance applies to a trade with "
            f"trade status '{record_data.get('trade_status')}', "
            f"security type '{record_data.get('security_type')}', "
            f"settlement date {record_data.get('settlement_date')}, "
            f"counterparty '{record_data.get('counterparty')}', "
            f"and settlement location '{record_data.get('settlement_location')}'?"
        )

    if record_type == "case_ticket":
        return (
            "What policy guidance applies to a case ticket with "
            f"category '{record_data.get('category')}', "
            f"priority '{record_data.get('priority')}', "
            f"status '{record_data.get('case_status')}', "
            f"assigned team '{record_data.get('assigned_team')}', "
            f"and SLA status '{record_data.get('sla_status')}'?"
        )

    return "What operational policy guidance applies to this record?"


def detect_guidance_domain(record_type: str | None) -> str | None:
    """
    Selects the best business domain filter for policy retrieval.

    Why this is useful:
    We do not want a settlement exception to retrieve corporate action policies.
    The domain filter keeps RAG focused on the right document family.
    """

    if record_type == "settlement_exception":
        return "settlement"

    if record_type == "reconciliation_break":
        return "reconciliation"

    if record_type == "trade":
        return "settlement"

    if record_type == "case_ticket":
        return None

    return None


def generate_operational_guidance(record_id: str, top_k: int = 8) -> dict:
    """
    Generates operational guidance for a trade, exception, break, or case.

    This connects:
    1. Azure SQL operational data
    2. RAG policy/SOP retrieval
    3. OpenAI answer generation
    4. Confidence score and citations

    This is a strong foundation for the future Operational Agent.
    """

    # Step 1: Build clean operational context from Azure SQL.
    operational_context = build_operational_context(record_id)

    # Step 2: If the record is not found, return a safe response.
    if not operational_context.get("found"):
        return {
            "record_id": record_id,
            "found": False,
            "message": operational_context.get("context_summary"),
            "operational_context": operational_context,
            "policy_guidance": None,
        }

    # Step 3: Convert operational record into a policy question.
    policy_question = build_policy_question_from_context(operational_context)

    # Step 4: Choose a domain filter based on record type.
    business_domain = detect_guidance_domain(
        operational_context.get("record_type")
    )

    # Step 5: Run RAG to generate policy guidance.
    policy_guidance = generate_rag_answer(
        query=policy_question,
        top_k=top_k,
        business_domain=business_domain,
    )

    # Step 6: Return combined operational context and policy guidance.
    return {
        "record_id": record_id,
        "found": True,
        "record_type": operational_context.get("record_type"),
        "context_summary": operational_context.get("context_summary"),
        "policy_question": policy_question,
        "business_domain": business_domain,
        "operational_context": operational_context,
        "policy_guidance": policy_guidance,
    }