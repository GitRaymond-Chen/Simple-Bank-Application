"""Domain exceptions and the handlers that map them to a consistent JSON error shape."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.models import utcnow
from app.schemas import ErrorResponse


class BankError(Exception):
    status_code = 400
    error = "BAD_REQUEST"

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class NotFoundError(BankError):
    status_code = 404
    error = "NOT_FOUND"


class InsufficientFundsError(BankError):
    status_code = 422
    error = "INSUFFICIENT_FUNDS"


class InvalidAmountError(BankError):
    status_code = 400
    error = "INVALID_AMOUNT"


def _error(status: int, error: str, message: str, details: list[dict] | None = None) -> JSONResponse:
    body = ErrorResponse(
        status=status, error=error, message=message, timestamp=utcnow(), details=details
    )
    return JSONResponse(status_code=status, content=body.model_dump(mode="json", exclude_none=True))


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(BankError)
    async def handle_bank_error(_: Request, exc: BankError) -> JSONResponse:
        return _error(exc.status_code, exc.error, exc.message)

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
        details = [
            {"field": ".".join(str(p) for p in e["loc"] if p != "body"), "message": e["msg"]}
            for e in exc.errors()
        ]
        return _error(400, "VALIDATION_ERROR", "Request validation failed", details)
