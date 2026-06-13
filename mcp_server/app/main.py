from mcp.server.fastmcp import FastMCP

from app.tools.operations_tools import (
    ask_policy_documents,
    get_operational_guidance,
    get_latest_memory_state,
)


# Create MCP server instance.
# This name is shown to MCP clients when they connect.
mcp = FastMCP("asset-servicing-copilot-mcp")


@mcp.tool()
async def operational_guidance(record_id: str, top_k: int = 8) -> dict:
    """
    Get operational guidance for an asset servicing record.

    Use this tool when the user asks about a specific operational record.

    Supported record IDs:
    - TRD-0000001 for trade records
    - EXC-000001 for settlement exceptions
    - BRK-0000001 for reconciliation breaks
    - CASE-0000001 for case tickets

    The tool returns:
    - live SQL operational context
    - RAG policy guidance
    - citations
    - confidence score
    - human review flag
    """

    return await get_operational_guidance(
        record_id=record_id,
        top_k=top_k,
    )


@mcp.tool()
async def policy_document_answer(
    query: str,
    top_k: int = 8,
    business_domain: str | None = None,
) -> dict:
    """
    Answer a policy or SOP question using indexed documents.

    Use this tool when the user asks a general policy, SOP, SLA,
    evidence, escalation, reconciliation, custody, settlement, or
    corporate-actions question without a specific operational record ID.

    Optional business_domain values:
    - settlement
    - reconciliation
    - custody
    - corporate_actions
    - sla_escalation

    The tool returns:
    - generated answer
    - citations
    - confidence score
    - human review flag
    """

    return await ask_policy_documents(
        query=query,
        top_k=top_k,
        business_domain=business_domain,
    )


@mcp.tool()
async def latest_memory_state(conversation_id: str) -> dict:
    """
    Get the latest saved memory state for a conversation.

    Use this tool when the user asks a follow-up question and the agent
    needs to recover previous context.

    The tool returns:
    - latest user query
    - previous route
    - record ID if available
    - business domain
    - confidence score
    - human review flag
    - response summary
    """

    return await get_latest_memory_state(
        conversation_id=conversation_id,
    )


if __name__ == "__main__":
    # Runs the MCP server using stdio transport by default.
    # This is the common local MCP development mode.
    mcp.run()