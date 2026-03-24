# DevHub n8n — Custom image met git + Python voor health checks
# Basis: n8n 2.12.3 (Alpine Linux)
FROM n8nio/n8n:2.12.3

USER root

# Installeer git (voor worktree), Python 3 en bash
RUN apk add --no-cache git python3 py3-pip bash

# Maak een venv voor DevHub check-tools (gescheiden van n8n's Node.js)
RUN python3 -m venv /opt/devhub-venv && \
    /opt/devhub-venv/bin/pip install --no-cache-dir \
        pytest>=8.0 \
        ruff>=0.4 \
        pip-audit \
        pyyaml>=6.0 \
        detect-secrets

USER node
