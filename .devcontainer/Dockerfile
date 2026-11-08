FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive

# Basics, plus what the JetBrains backend needs (curl, unzip, ps, X/font libs).
# No sudo, no docker, no ssh, no AWS.
RUN apt-get update && apt-get install -y --no-install-recommends \
      git curl ca-certificates unzip procps ripgrep less jq nano \
      libxext6 libxrender1 libxtst6 libxi6 libfreetype6 \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -s /bin/bash developer \
    && mkdir -p /workspace /home/developer/.claude \
    && chown -R developer:developer /workspace /home/developer/.claude

USER developer
WORKDIR /workspace
CMD ["sleep", "infinity"]
