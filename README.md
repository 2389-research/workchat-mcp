# WorkChat

A real-time team chat application built with FastAPI.

## Development Setup

1. Install dependencies:
   ```bash
   uv sync --dev
   ```

2. Run the development server:
   ```bash
   uv run python main.py
   ```

3. Run tests:
   ```bash
   uv run pytest
   ```

4. Run linting:
   ```bash
   uv run ruff check .
   uv run black --check .
   uv run isort --check .
   ```

## API Documentation

Once the server is running, visit:
- http://localhost:8000/docs for interactive API documentation
- http://localhost:8000/redoc for ReDoc documentation