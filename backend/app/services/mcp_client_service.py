import json
import os
import sys
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


def get_project_root() -> Path:
    """
    Current file:
    backend/app/services/mcp_client_service.py

    parents[0] = services
    parents[1] = app
    parents[2] = backend
    parents[3] = project root
    """

    return Path(__file__).resolve().parents[3]


def get_mcp_server_main_path() -> Path:
    """
    Root MCP server path:
    mcp_server/app/main.py
    """

    return get_project_root() / "mcp_server" / "app" / "main.py"


def parse_mcp_tool_result(result: Any) -> dict:
    """
    Converts MCP tool response into normal dict.

    MCP returns content blocks. Most JSON results come back as text.
    """

    if not hasattr(result, "content"):
        return {"raw_result": str(result)}

    if not result.content:
        return {}

    first_content = result.content[0]
    text_value = getattr(first_content, "text", None)

    if text_value is None:
        return {"raw_result": str(first_content)}

    try:
        return json.loads(text_value)
    except json.JSONDecodeError:
        return {"text": text_value}


async def call_mcp_tool(tool_name: str, arguments: dict) -> dict:
    """
    FastAPI backend starts MCP automatically using stdio.

    Flow:
    Backend
      -> MCP client
      -> root/mcp_server/app/main.py
      -> MCP tool
      -> backend API
    """

    project_root = get_project_root()
    mcp_main_path = get_mcp_server_main_path()

    if not mcp_main_path.exists():
        raise FileNotFoundError(f"MCP server main.py not found: {mcp_main_path}")

    mcp_server_root = project_root / "mcp_server"

    server_params = StdioServerParameters(
        command=sys.executable,
        args=[str(mcp_main_path)],
        env={
            **os.environ,
            "PYTHONPATH": str(mcp_server_root),
            "BACKEND_API_BASE_URL": os.getenv(
                "BACKEND_API_BASE_URL",
                "http://127.0.0.1:8000",
            ),
        },
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            result = await session.call_tool(
                tool_name,
                arguments=arguments,
            )

            return parse_mcp_tool_result(result)


async def mcp_operational_guidance(record_id: str, top_k: int = 8) -> dict:
    """
    Calls MCP tool: operational_guidance
    """

    return await call_mcp_tool(
        tool_name="operational_guidance",
        arguments={
            "record_id": record_id,
            "top_k": top_k,
        },
    )


async def mcp_policy_document_answer(
    query: str,
    top_k: int = 8,
    business_domain: str | None = None,
) -> dict:
    """
    Calls MCP tool: policy_document_answer
    """

    arguments = {
        "query": query,
        "top_k": top_k,
    }

    if business_domain:
        arguments["business_domain"] = business_domain

    return await call_mcp_tool(
        tool_name="policy_document_answer",
        arguments=arguments,
    )


async def mcp_latest_memory_state(conversation_id: str) -> dict:
    """
    Calls MCP tool: latest_memory_state
    """

    return await call_mcp_tool(
        tool_name="latest_memory_state",
        arguments={
            "conversation_id": conversation_id,
        },
    )