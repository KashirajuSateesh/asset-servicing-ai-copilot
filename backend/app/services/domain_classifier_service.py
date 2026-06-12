def detect_business_domain(query: str) -> str | None:
    """
    Detects the most likely business domain from the user query.

    Why we need this:
    The user should not have to manually pass business_domain every time.
    This function helps the RAG pipeline automatically filter retrieval
    to the most relevant document family.

    Current approach:
    - Simple keyword-based detection.
    - This is easy to explain and reliable for our demo.
    - Later, the orchestrator agent can replace this with LLM-based routing.

    Possible return values:
    - settlement
    - reconciliation
    - custody
    - corporate_actions
    - sla_escalation
    - None
    """

    # Convert query to lowercase so matching is case-insensitive.
    query_lower = query.lower()

    # Settlement-related questions.
    settlement_keywords = [
        "settlement",
        "failed settlement",
        "trade fail",
        "failed trade",
        "settlement exception",
        "counterparty hold",
        "trade status",
    ]

    # Reconciliation-related questions.
    reconciliation_keywords = [
        "reconciliation",
        "recon",
        "break",
        "cash break",
        "position break",
        "variance",
        "ledger",
    ]

    # Custody account-related questions.
    custody_keywords = [
        "custody",
        "custodian",
        "account servicing",
        "account checks",
        "kyc",
        "onboarding",
        "account status",
    ]

    # Corporate actions-related questions.
    corporate_action_keywords = [
        "corporate action",
        "election",
        "dividend",
        "entitlement",
        "record date",
        "payable date",
        "ex date",
    ]

    # SLA and client communication-related questions.
    sla_keywords = [
        "sla",
        "breach",
        "client communication",
        "client inquiry",
        "escalation",
        "response time",
        "manager review",
    ]

    # Check more specific domains first.
    # Settlement + escalation should usually stay settlement because the user
    # is asking about settlement operation rules.
    if any(keyword in query_lower for keyword in settlement_keywords):
        return "settlement"

    if any(keyword in query_lower for keyword in reconciliation_keywords):
        return "reconciliation"

    if any(keyword in query_lower for keyword in custody_keywords):
        return "custody"

    if any(keyword in query_lower for keyword in corporate_action_keywords):
        return "corporate_actions"

    if any(keyword in query_lower for keyword in sla_keywords):
        return "sla_escalation"

    # If no clear domain is found, return None.
    # Then the RAG service can search across all documents.
    return None