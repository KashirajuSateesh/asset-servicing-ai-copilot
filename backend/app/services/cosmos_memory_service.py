from datetime import datetime, timezone
from uuid import uuid4

from azure.cosmos import CosmosClient, PartitionKey
from azure.cosmos.exceptions import CosmosResourceNotFoundError

from app.config import settings


def get_cosmos_container():
    """
    Creates a Cosmos DB container client.

    This client points to:
    - Cosmos account endpoint
    - database: asset_copilot_memory
    - container: agent_state

    The container stores agent state and conversation memory.
    """

    if not settings.azure_cosmos_endpoint or not settings.azure_cosmos_key:
        raise ValueError("Azure Cosmos DB endpoint or key is missing.")

    client = CosmosClient(
        url=settings.azure_cosmos_endpoint,
        credential=settings.azure_cosmos_key,
    )

    database = client.get_database_client(settings.azure_cosmos_database)
    container = database.get_container_client(settings.azure_cosmos_container)

    return container


def utc_now_iso() -> str:
    """
    Returns current UTC time as an ISO string.

    We store timestamps in UTC so records are consistent across environments.
    """

    return datetime.now(timezone.utc).isoformat()


def save_agent_state(
    conversation_id: str,
    user_query: str,
    route: str,
    response_summary: str | None = None,
    record_id: str | None = None,
    business_domain: str | None = None,
    confidence_score: float | None = None,
    confidence_label: str | None = None,
    human_review_required: bool | None = None,
) -> dict:
    """
    Saves one agent/orchestrator state event into Cosmos DB.

    Each user query creates a new state document.

    Why this is useful:
    - Keeps a history of user questions.
    - Stores which route the orchestrator selected.
    - Stores record ID, business domain, confidence, and review flag.
    - Helps future follow-up questions use previous context.
    """

    container = get_cosmos_container()

    state_document = {
        "id": f"state_{uuid4()}",
        "conversation_id": conversation_id,
        "user_query": user_query,
        "route": route,
        "record_id": record_id,
        "business_domain": business_domain,
        "confidence_score": confidence_score,
        "confidence_label": confidence_label,
        "human_review_required": human_review_required,
        "response_summary": response_summary,
        "created_at": utc_now_iso(),
        "updated_at": utc_now_iso(),
    }

    container.create_item(body=state_document)

    return state_document


def get_latest_agent_state(conversation_id: str) -> dict | None:
    """
    Gets the latest saved state document for a conversation.

    This will be useful for follow-up questions.

    Example:
    User first asks:
    "What should I do for EXC-000001?"

    Then user asks:
    "What should I do next?"

    The orchestrator can fetch the latest state and understand that
    the current conversation was about EXC-000001.
    """

    container = get_cosmos_container()

    query = """
    SELECT * FROM c
    WHERE c.conversation_id = @conversation_id
    ORDER BY c.created_at DESC
    """

    parameters = [
        {
            "name": "@conversation_id",
            "value": conversation_id,
        }
    ]

    results = list(
        container.query_items(
            query=query,
            parameters=parameters,
            partition_key=conversation_id,
            max_item_count=1,
        )
    )

    if not results:
        return None

    return results[0]


def list_agent_states(conversation_id: str, limit: int = 10) -> list[dict]:
    """
    Lists recent state documents for a conversation.

    This is useful for debugging and seeing what memory the agent saved.
    """

    container = get_cosmos_container()

    query = """
    SELECT * FROM c
    WHERE c.conversation_id = @conversation_id
    ORDER BY c.created_at DESC
    """

    parameters = [
        {
            "name": "@conversation_id",
            "value": conversation_id,
        }
    ]

    results = list(
        container.query_items(
            query=query,
            parameters=parameters,
            partition_key=conversation_id,
            max_item_count=limit,
        )
    )

    return results[:limit]