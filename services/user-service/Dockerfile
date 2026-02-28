FROM python:3.12-slim

# Install uv for fast dependency resolution
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set working directory
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies (without installing the project itself yet)
RUN uv sync --frozen --no-install-project --no-dev

# Copy the rest of the application code
COPY . .

# Expose the application port
EXPOSE 8000

# Command to run the application
CMD ["uv", "run", "fastapi", "run", "app/main.py", "--port", "8000", "--host", "0.0.0.0"]
