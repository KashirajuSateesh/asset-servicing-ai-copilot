from mcp.server.fastmcp import FastMCP

from app.tools.operations_tools import get_operational_guidance


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


if __name__ == "__main__":
    # Runs the MCP server using stdio transport by default.
    # This is the common local MCP development mode.
    mcp.run()