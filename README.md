# Asset Servicing AI Copilot

A GenAI-powered asset servicing operations copilot for policy lookup, settlement exception analysis, reconciliation break investigation, and case support.

## Project Goal

This project recreates an enterprise-style financial operations AI copilot using synthetic asset servicing data. It combines RAG, SQL-based operational lookup, MCP tools, agent orchestration, and citation-backed responses.

## Core Capabilities

- Ask policy and SOP questions with citations
- Analyze settlement exceptions
- Investigate reconciliation breaks
- Search trade, case, and account records
- Generate confidence-scored answers
- Log agent tool calls and audit activity

## Tech Stack

- Frontend: Next.js, Tailwind CSS
- Backend: FastAPI, Uvicorn
- Package Management: uv
- Agents: OpenAI Agents SDK
- MCP: Custom MCP server
- Database: Azure SQL
- File Storage: Azure Blob Storage
- Vector Search: Azure AI Search
- LLM and Embeddings: OpenAI API

## Project Structure

```text
asset-servicing-ai-copilot/
├── frontend/
├── backend/
├── mcp_server/
├── ingestion/
├── data/
├── infrastructure/
├── docs/
└── README.md