from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


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
