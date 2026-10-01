from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import get_db, init_db
from app.routers import users, accounts
from app.exceptions import register_exception_handlers


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create MongoDB indexes on startup (no-op if they already exist).
    # Done here rather than at import time so tests can import the app
    # without a database connection.
    init_db(get_db())
    yield


app = FastAPI(title="Simple Bank API", version="1.0.0", lifespan=lifespan)

# Allow requests from React dev servers
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register custom error handlers (NotFoundError → 404, etc.)
register_exception_handlers(app)

# Mount routers — all endpoints are prefixed with /api
app.include_router(users.router)
app.include_router(accounts.router)


@app.get("/")
def health_check():
    """Health check endpoint — confirms the API is running."""
    return {"status": "ok"}
