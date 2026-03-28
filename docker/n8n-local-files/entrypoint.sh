#!/bin/bash
# Install devhub packages from mounted repo (read-only mount, no -e flag).
# Order matters: devhub-core first (base dependency), then the rest.
if [ -d "/repo/packages/devhub-core" ]; then
    pip install --no-cache-dir --quiet /repo/packages/devhub-core 2>/dev/null || true
    pip install --no-cache-dir --quiet --no-deps \
        /repo/packages/devhub-storage \
        /repo/packages/devhub-vectorstore \
        /repo/packages/devhub-documents \
        2>/dev/null || true
fi

exec uvicorn dev_os_api:app --host 0.0.0.0 --port 8001
