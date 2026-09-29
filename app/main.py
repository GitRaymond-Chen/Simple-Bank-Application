from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.dependencies import build_container
from app.exceptions import register_exception_handlers
from app.routers import accounts, users


def create_app() -> FastAPI:
    app = FastAPI(
        title="Simple Bank API",
        version="0.1.0",
        description="Create accounts, deposit, withdraw and view transaction history. "
        "In-memory storage: data resets when the server restarts.",
    )
    app.state.container = build_container()

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://localhost:3000"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_exception_handlers(app)
    app.include_router(users.router)
    app.include_router(accounts.router)

    @app.get("/health", tags=["Health"])
    def health():
        return {"status": "ok"}

    return app


app = create_app()
