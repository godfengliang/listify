#!/bin/sh
# Railway Docker entrypoint — uses PORT env var if set, defaults to 8000
exec python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}