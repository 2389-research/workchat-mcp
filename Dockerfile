# ABOUTME: Multi-stage Docker build for WorkChat application
# ABOUTME: Optimized for production deployment with minimal final image size

# Build stage - use UV for fast dependency resolution
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim as builder

# Set working directory
WORKDIR /app

# Copy dependency files and source code for package build
COPY pyproject.toml uv.lock README.md ./
COPY workchat/ ./workchat/

# Install dependencies to virtual environment (production only)
RUN uv sync --frozen --no-cache --no-dev

# Production stage - minimal runtime image
FROM debian:bookworm-slim

# Install UV for runtime and minimal system dependencies
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash workchat

# Set working directory
WORKDIR /app

# Copy virtual environment from builder stage
COPY --from=builder /app/.venv /app/.venv

# Copy application code
COPY --chown=workchat:workchat . /app

# Switch to non-root user
USER workchat

# Ensure we use the virtual environment
ENV PATH="/app/.venv/bin:$PATH"

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "workchat.app:app", "--host", "0.0.0.0", "--port", "8000"]