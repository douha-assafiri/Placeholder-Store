FROM python:3.14.7-slim
LABEL authors="Adam Hanna"

WORKDIR /api

# Install UV for package manager
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock* ./
RUN uv sync --no-dev
COPY . .

EXPOSE 8000

CMD ["uvicorn", "account:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]