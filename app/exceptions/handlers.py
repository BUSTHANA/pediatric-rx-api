from fastapi import Request
from fastapi.responses import JSONResponse


# --- Custom Exception Classes ---

class AIRateLimitError(Exception):
    """Raised when Gemini API quota/rate limit is exceeded."""
    pass


class AIResponseError(Exception):
    """Raised when Gemini returns an unparsable or invalid response."""
    pass


class AIServiceUnavailableError(Exception):
    """Raised when Gemini API is unreachable (network/connection issues)."""
    pass


# --- Exception Handlers (registered with FastAPI app) ---

async def rate_limit_handler(request: Request, exc: AIRateLimitError):
    return JSONResponse(
        status_code=429,
        content={
            "error": "rate_limit",
            "message": "Our AI service is temporarily busy. Please try again in a minute.",
        },
    )


async def ai_response_handler(request: Request, exc: AIResponseError):
    return JSONResponse(
        status_code=502,
        content={
            "error": "ai_response_error",
            "message": "We couldn't process the AI response. Please try again.",
        },
    )


async def ai_unavailable_handler(request: Request, exc: AIServiceUnavailableError):
    return JSONResponse(
        status_code=503,
        content={
            "error": "service_unavailable",
            "message": "The AI service is currently unavailable. Please try again later.",
        },
    )


async def general_error_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_error",
            "message": "Something went wrong on our end. Please try again later.",
        },
    )


def register_exception_handlers(app):
    """Register all custom exception handlers with the FastAPI app."""
    app.add_exception_handler(AIRateLimitError, rate_limit_handler)
    app.add_exception_handler(AIResponseError, ai_response_handler)
    app.add_exception_handler(AIServiceUnavailableError, ai_unavailable_handler)
    app.add_exception_handler(Exception, general_error_handler)
