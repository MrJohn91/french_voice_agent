FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    python3-dev \
    ffmpeg \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml ./
COPY uv.lock ./

RUN uv sync

COPY agent.py ./

CMD ["uv", "run", "agent.py", "start"]
