from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pymongo.errors import DuplicateKeyError, ServerSelectionTimeoutError


# ── Custom Exception Classes ──────────────────────────────────

class NotFoundError(Exception):
    """Raised when a requested resource (user, account) does not exist."""
    def __init__(self, message: str = "Resource not found"):
        self.message = message
        super().__init__(message)


class InsufficientFundsError(Exception):
    """Raised when a withdrawal would make the balance negative."""
    def __init__(self, message: str = "Insufficient funds"):
        self.message = message
        super().__init__(message)


class InvalidAmountError(Exception):
    """Raised when a deposit or withdrawal amount is zero or negative."""
    def __init__(self, message: str = "Amount must be greater than zero"):
        self.message = message
        super().__init__(message)


# ── Exception Handlers ────────────────────────────────────────

def register_exception_handlers(app: FastAPI) -> None:
    """
    Attach custom exception handlers to the FastAPI app so that
    our custom errors are automatically converted to JSON responses.
    Every error body is {"detail": "<message>"} so the frontend can show it directly.
    """

    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError):
        return JSONResponse(status_code=404, content={"detail": exc.message})

    @app.exception_handler(InsufficientFundsError)
    async def insufficient_funds_handler(request: Request, exc: InsufficientFundsError):
        return JSONResponse(status_code=400, content={"detail": exc.message})

    @app.exception_handler(InvalidAmountError)
    async def invalid_amount_handler(request: Request, exc: InvalidAmountError):
        return JSONResponse(status_code=400, content={"detail": exc.message})

    @app.exception_handler(DuplicateKeyError)
    async def duplicate_key_handler(request: Request, exc: DuplicateKeyError):
        # e.g. two requests racing to register the same email (unique index)
        return JSONResponse(status_code=409, content={"detail": "Conflicts with existing data"})

    @app.exception_handler(ServerSelectionTimeoutError)
    async def db_unavailable_handler(request: Request, exc: ServerSelectionTimeoutError):
        # Atlas unreachable: wrong URI, IP not on the access list, or cluster paused
        return JSONResponse(status_code=503, content={"detail": "Database unavailable"})

    @app.exception_handler(RequestValidationError)
    async def validation_handler(request: Request, exc: RequestValidationError):
        # FastAPI's default is a list of error objects; flatten to one readable string
        messages = []
        for err in exc.errors():
            field = ".".join(str(p) for p in err["loc"] if p != "body")
            messages.append(f"{field}: {err['msg']}" if field else err["msg"])
        return JSONResponse(status_code=400, content={"detail": "; ".join(messages)})
