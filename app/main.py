"""Listify - AI Multi-Platform Listing Generator."""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router

app = FastAPI(title="Listify", version="0.2.0")

# CORS for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory rate limiter
_rate_limits: dict[str, list[float]] = {}
import time as _time


@app.middleware("http")
async def rate_limit(request: Request, call_next):
    """Simple rate limiter: 60 requests per minute per IP."""
    client_ip = request.client.host if request.client else "unknown"
    now = _time.time()
    window = now - 60

    if client_ip not in _rate_limits:
        _rate_limits[client_ip] = []

    # Clean old entries
    _rate_limits[client_ip] = [t for t in _rate_limits[client_ip] if t > window]

    if len(_rate_limits[client_ip]) >= 60:
        from fastapi.responses import JSONResponse
        return JSONResponse({"detail": "请求太频繁，请稍后再试"}, status_code=429)

    _rate_limits[client_ip].append(now)
    return await call_next(request)


app.include_router(router)
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/")
async def index():
    return FileResponse("app/static/index.html")
