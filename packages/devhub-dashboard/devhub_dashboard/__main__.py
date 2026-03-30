"""Allow running the dashboard via `python -m devhub_dashboard`.

Use --fastapi flag or DEVHUB_DASHBOARD_ENGINE=fastapi env var
to start the FastAPI+HTMX version instead of NiceGUI.
"""

import os
import sys


def _use_fastapi() -> bool:
    if "--fastapi" in sys.argv:
        return True
    return os.environ.get("DEVHUB_DASHBOARD_ENGINE", "").lower() == "fastapi"


if _use_fastapi():
    import uvicorn

    from devhub_dashboard.config import DashboardConfig

    config = DashboardConfig()
    uvicorn.run(
        "devhub_dashboard.fastapi_app:app",
        host=config.host,
        port=config.port,
        reload=False,
    )
else:
    from devhub_dashboard.app import main

    main()
