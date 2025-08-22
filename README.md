# WorkChat

A real-time team chat application built with FastAPI, SQLModel, and modern web technologies.

## Features

- **Real-time messaging** with Server-Sent Events (SSE)
- **Channel-based organization** with threaded conversations  
- **Full-text search** using SQLite FTS5
- **Comprehensive audit logging** for all message operations
- **MCP (Model Context Protocol) integration** for AI assistant access
- **JWT-based authentication** with role-based access control
- **Multi-tenant organization support**

## Quick Start

### Using Docker Compose

```bash
docker compose up
```

The application will be available at http://localhost:8000

### Backend Development

1. Install dependencies:
   ```bash
   uv sync
   ```

2. Run database migrations:
   ```bash
   uv run alembic upgrade head
   ```

3. Start the backend server:
   ```bash
   uv run uvicorn workchat.app:app --reload
   ```

### Frontend Development

1. Install frontend dependencies:
   ```bash
   cd frontend && npm install
   ```

2. Start the frontend development server:
   ```bash
   npm run dev
   ```

Frontend will be available at http://localhost:3000 with backend proxy.

### MCP Server Mode

For AI assistant integration:

```bash
python -m workchat.mcp
```

## Development

### Testing

#### Backend Tests
```bash
uv run pytest
```

#### Frontend E2E Tests
```bash
cd frontend
npm ci
npx playwright install
npm run test:e2e
```

### Linting

```bash
uv run ruff check .
uv run ruff format --check .
uv run isort --check .
```

## API Documentation

Interactive API documentation is available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Architecture

- **FastAPI** - Web framework and API layer
- **SQLModel** - Database ORM and schema validation  
- **SQLite** - Database with FTS5 search
- **FastMCP** - Model Context Protocol integration
- **Alembic** - Database migrations
- **JWT** - Authentication and authorization

## License

MIT License