#!/bin/bash
# Install devhub packages from mounted repo (if available)
if [ -d "/repo/packages/devhub-core" ]; then
    pip install --no-cache-dir -e /repo/packages/devhub-core 2>/dev/null || true
fi

exec uvicorn dev_os_api:app --host 0.0.0.0 --port 8001
