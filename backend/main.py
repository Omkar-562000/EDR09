from __future__ import annotations

import uvicorn


def run() -> None:
    """Run the EDR backend with real Windows data collection."""
    uvicorn.run("backend.edr.api.app:app", host="127.0.0.1", port=8000, reload=False)


if __name__ == "__main__":
    run()
