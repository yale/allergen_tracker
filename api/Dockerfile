FROM python:3.12-slim

WORKDIR /app

# Install uv for fast dependency management
RUN pip install uv

# Copy dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-dev

# Copy application code
COPY src/ ./src/

# Create cache directory
RUN mkdir -p /app/cache

EXPOSE 8000

# Run with uv
CMD ["uv", "run", "python", "src/main.py"]
