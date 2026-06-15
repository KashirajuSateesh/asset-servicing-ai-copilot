FROM python:3.12-slim

WORKDIR /app

# Install system dependencies and Microsoft ODBC Driver 18 for SQL Server.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        gnupg \
        apt-transport-https \
        ca-certificates \
        unixodbc \
        unixodbc-dev \
        gcc \
        g++ \
    && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc \
        | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
    && curl -fsSL https://packages.microsoft.com/config/debian/12/prod.list \
        -o /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql18 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install uv.
RUN pip install --no-cache-dir uv

# Copy backend dependency files first.
COPY backend/pyproject.toml backend/uv.lock /app/backend/

WORKDIR /app/backend

# Install backend Python dependencies.
RUN uv sync --locked --no-dev

# Copy backend code.
COPY backend /app/backend

# Copy MCP server code from root into container.
COPY mcp_server /app/mcp_server

# Render provides PORT environment variable.
CMD ["sh", "-c", "uv run uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}"]