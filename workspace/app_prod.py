
# pyproject.toml

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "secure-calculator"
version = "1.0.0"
description = "A secure, production-grade Python calculator service."
authors = [{ name = "Senior Python Developer" }]
requires-python = ">=3.10"
classifiers = [
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
dependencies = [
    "asteval==0.9.31",
    "fastapi==0.111.0",
    "uvicorn[standard]==0.29.0",
    "pydantic-settings==2.2.1",
    "slowapi==0.1.9",
    "structlog==24.1.0",
    "python-json-logger==2.0.7",
]

[project.optional-dependencies]
test = [
    "pytest==8.2.0",
    "pytest-cov==5.0.0",
    "httpx==0.27.0",
]

[project.scripts]
calculator-cli = "calculator.cli:main"
calculator-api = "calculator.api.main:run"

[tool.hatch.build.targets.wheel]
packages = ["calculator"]


# calculator/exceptions.py

class CalculatorError(Exception):
    """Base exception for all calculator-related errors."""
    pass


class ValidationError(CalculatorError):
    """Raised for invalid input expressions."""
    pass


class CalculationError(CalculatorError):
    """Raised for mathematical errors during evaluation."""
    pass


# calculator/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""
    # Core Engine Settings
    MAX_EXPRESSION_LENGTH: int = 1024
    EVALUATION_TIMEOUT_SECONDS: float = 1.0

    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_WORKERS: int = 1
    API_RATE_LIMIT: str = "100/minute"

    # Logging Settings
    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8', extra="ignore")


settings = Settings()


# calculator/engine.py

import re
import signal
from contextlib import contextmanager
from typing import final

from asteval import Interpreter

from calculator.config import settings
from calculator.exceptions import CalculationError, ValidationError


@contextmanager
def timeout(seconds: float):
    """A context manager to enforce a timeout on a block of code."""

    def signal_handler(signum, frame):
        raise TimeoutError(f"Evaluation timed out after {seconds} seconds")

    if not hasattr(signal, 'SIGALRM'):
        # Windows does not support SIGALRM
        yield
        return

    signal.signal(signal.SIGALRM, signal_handler)
    # Set the alarm. Floats are accepted from Python 3.5.
    signal.setitimer(signal.ITIMER_REAL, seconds)
    try:
        yield
    finally:
        # Disable the alarm
        signal.setitimer(signal.ITIMER_REAL, 0)


@final
class CalculatorEngine:
    """
    A secure, sandboxed engine for evaluating mathematical expressions.
    """
    # NFR-1.2: Stricly validate input against allowed characters.
    _ALLOWED_CHARS_PATTERN = re.compile(r"^[0-9\s.()+\-*/^]*$")

    def __init__(self, timeout_seconds: float = settings.EVALUATION_TIMEOUT_SECONDS):
        self._timeout_seconds = timeout_seconds
        # NFR-1.1: Use a safe, sandboxed AST-based interpreter.
        self._interpreter = self._create_sandboxed_interpreter()

    def _create_sandboxed_interpreter(self) -> Interpreter:
        """
        Creates a sandboxed asteval interpreter with no built-ins or
        unsafe functions.
        """
        # Start with an empty symbol table, no built-ins.
        aeval = Interpreter(symtable={}, use_builtin_funcs=False)

        # asteval is safe by default and does not allow access to attributes
        # or subscripting. The following are extra precautions.
        for node_type in (
            'Import', 'ImportFrom', 'Call', 'Attribute',
            'Subscript', 'Lambda', 'ListComp', 'DictComp',
            'SetComp', 'GeneratorExp'
        ):
            if node_type in aeval.node_handlers:
                del aeval.node_handlers[node_type]

        return aeval

    def evaluate(self, expression: str) -> float:
        """
        Safely evaluates a mathematical expression string.

        Args:
            expression: The mathematical expression to evaluate.

        Returns:
            The result of the evaluation as a float.

        Raises:
            ValidationError: If the expression is invalid, too long, or
                             contains disallowed characters.
            CalculationError: If a mathematical error occurs (e.g.,
                              division by zero) or evaluation times out.
        """
        self._validate_input(expression)

        # FR-1.2: Support both ** and ^ for exponentiation
        processed_expression = expression.replace('^', '**')

        try:
            with timeout(self._timeout_seconds):
                result = self._interpreter.eval(processed_expression)

            if not isinstance(result, (int, float)):
                raise CalculationError("Evaluation resulted in a non-numeric type.")

            return float(result)

        except TimeoutError as e:
            raise CalculationError(str(e)) from e
        except ZeroDivisionError:
            raise CalculationError("Division by zero is not allowed.")
        except OverflowError:
            raise CalculationError("Calculation resulted in a number too large to represent.")
        except Exception as e:
            # Catch other potential asteval or Python errors and wrap them.
            # NFR-1.4: Avoid leaking internal details.
            raise ValidationError(f"Invalid expression: {e}")

    def _validate_input(self, expression: str) -> None:
        """
        Performs pre-evaluation checks on the expression string.
        """
        if not isinstance(expression, str) or not expression.strip():
            raise ValidationError("Expression must be a non-empty string.")

        # NFR-1.3: Enforce maximum expression length.
        if len(expression) > settings.MAX_EXPRESSION_LENGTH:
            raise ValidationError(
                f"Expression exceeds maximum length of {settings.MAX_EXPRESSION_LENGTH} characters."
            )

        if not self._ALLOWED_CHARS_PATTERN.match(expression):
            raise ValidationError("Expression contains disallowed characters.")


# calculator/logging_config.py

import logging
import sys

from calculator.config import settings


def setup_logging():
    """Configures structured logging for the application."""
    log_level = settings.LOG_LEVEL.upper()
    logging.basicConfig(stream=sys.stdout, level=log_level, format="%(message)s")

    # Configure root logger for structured logging
    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        root_logger.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s - [correlation_id: %(correlation_id)s]"
        )
    )

    # Use a filter to add correlation_id to all log records
    class CorrelationIdFilter(logging.Filter):
        def filter(self, record):
            # This will be set by the API middleware
            record.correlation_id = getattr(record, 'correlation_id', 'N/A')
            return True

    root_logger.addHandler(handler)
    root_logger.addFilter(CorrelationIdFilter())
    root_logger.setLevel(log_level)

    # Silence overly verbose third-party loggers
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


# calculator/api/models.py

from pydantic import BaseModel, Field, constr

from calculator.config import settings

# A regular expression that matches a valid expression string,
# enforcing the same character set as the engine.
EXPRESSION_REGEX = r"^[0-9\s.()+\-*/^]*$"


class CalculationRequest(BaseModel):
    expression: constr(
        strip_whitespace=True,
        min_length=1,
        max_length=settings.MAX_EXPRESSION_LENGTH,
        pattern=EXPRESSION_REGEX,
    )


class CalculationResponse(BaseModel):
    result: float
    expression: str


class HealthResponse(BaseModel):
    status: str = "ok"


class ErrorResponse(BaseModel):
    error: str


# calculator/api/main.py

import logging
import time
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from calculator.api.models import (CalculationRequest, CalculationResponse,
                                   ErrorResponse, HealthResponse)
from calculator.config import settings
from calculator.engine import CalculatorEngine
from calculator.exceptions import CalculationError, ValidationError
from calculator.logging_config import setup_logging

# --- Configuration & Initialization ---

# NFR-4.3: Setup structured logging
setup_logging()
logger = logging.getLogger(__name__)

# NFR-1.6: Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage the application's lifespan."""
    app.state.engine = CalculatorEngine()
    app.state.limiter = limiter
    logger.info("Calculator API service started.")
    yield
    logger.info("Calculator API service shutting down.")

app = FastAPI(
    title="Secure Production Calculator",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/",
    redoc_url=None,
)

# --- Middleware ---

# NFR-1.6: Apply rate limiting to the app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    """
    NFR-4.4: Injects a correlation ID into the request state and log context
    for request tracing. Also logs request timing.
    """
    correlation_id = str(uuid.uuid4())
    # Attach to request state for access in endpoints
    request.state.correlation_id = correlation_id

    # Create a logger adapter to inject correlation_id into all log messages
    logger_adapter = logging.LoggerAdapter(logger, {'correlation_id': correlation_id})

    start_time = time.perf_counter()

    # Pass the logger adapter down through the request state if needed elsewhere
    request.state.logger = logger_adapter

    response = await call_next(request)

    process_time = (time.perf_counter() - start_time) * 1000
    response.headers["X-Correlation-ID"] = correlation_id
    response.headers["X-Process-Time-ms"] = f"{process_time:.2f}"

    logger_adapter.info(
        f"Request finished",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "process_time_ms": f"{process_time:.2f}"
        }
    )
    return response

# --- Exception Handlers ---

@app.exception_handler(ValidationError)
async def validation_error_handler(request: Request, exc: ValidationError):
    """Handles input validation errors from the engine."""
    request.state.logger.warning(f"Validation error: {exc}")
    return JSONResponse(
        status_code=400,
        content={"error": str(exc)},
    )


@app.exception_handler(CalculationError)
async def calculation_error_handler(request: Request, exc: CalculationError):
    """Handles mathematical errors from the engine."""
    request.state.logger.warning(f"Calculation error: {exc}")
    return JSONResponse(
        status_code=400,
        content={"error": str(exc)},
    )


@app.exception_handler(RequestValidationError)
async def pydantic_validation_error_handler(request: Request, exc: RequestValidationError):
    """Handles Pydantic's request validation errors for a cleaner response."""
    request.state.logger.warning(f"Request validation failed: {exc.errors()}")
    # Provide a simple, user-friendly message
    return JSONResponse(
        status_code=400,
        content={"error": "Invalid request body or parameters."},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """
    Handles any unexpected errors, preventing stack traces from leaking.
    NFR-1.4: Secure error handling.
    """
    request.state.logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "An internal server error occurred."},
    )


# --- API Endpoints ---

@app.get(
    "/health",
    tags=["Monitoring"],
    summary="Performs a health check of the service.",
    response_model=HealthResponse,
)
async def health_check():
    """FR-3.1: Health check endpoint."""
    return {"status": "ok"}


@app.post(
    "/calculate",
    tags=["Calculator"],
    summary="Evaluates a mathematical expression.",
    response_model=CalculationResponse,
    responses={400: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
@limiter.limit(settings.API_RATE_LIMIT)
async def calculate(request: Request, body: CalculationRequest):
    """
    FR-3.2: Accepts a JSON object with an "expression" key and returns the
    calculated result.
    """
    engine: CalculatorEngine = request.app.state.engine
    expression = body.expression

    request.state.logger.info(f"Received calculation request for expression.")
    # Note: Expression itself is not logged to prevent logging sensitive data (NFR-4.4)

    result = engine.evaluate(expression)

    return CalculationResponse(result=result, expression=expression)


def run():
    """Entrypoint for running the API server with Uvicorn."""
    import uvicorn
    uvicorn.run(
        "calculator.api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        workers=settings.API_WORKERS,
        log_level=settings.LOG_LEVEL.lower(),
    )


# calculator/cli.py

import argparse
import sys

from calculator.config import settings
from calculator.engine import CalculatorEngine
from calculator.exceptions import CalculatorError


def main():
    """
    Command-Line Interface entrypoint for the calculator.
    """
    # FR-2.5: Provide usage information with --help
    parser = argparse.ArgumentParser(
        description="A secure command-line calculator.",
        epilog="Example: calculator-cli \"5 * (10 + 2)\""
    )
    # FR-2.2: Accept expression as a single string argument
    parser.add_argument(
        "expression",
        type=str,
        help="The mathematical expression to evaluate, enclosed in quotes.",
    )
    args = parser.parse_args()

    try:
        engine = CalculatorEngine(timeout_seconds=settings.EVALUATION_TIMEOUT_SECONDS)
        result = engine.evaluate(args.expression)

        # FR-2.3: Print result to stdout on success
        print(result)
        sys.exit(0)

    except CalculatorError as e:
        # FR-2.4: Print clear error to stderr on failure
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        # NFR-1.4: Catch-all to prevent stack traces
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()


# Dockerfile

# --- Stage 1: Builder ---
# Use a full Python image to build dependencies, which may require build tools.
FROM python:3.11-slim-bookworm as builder

# Set working directory
WORKDIR /app

# Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE 1
# Ensure Python output is sent straight to the terminal without buffering
ENV PYTHONUNBUFFERED 1

# Install Poetry for dependency management (alternative to pip with pyproject.toml)
# This provides more robust dependency resolution.
RUN pip install --no-cache-dir poetry

# Copy only the dependency definition files
COPY pyproject.toml poetry.lock* ./

# Install project dependencies into a virtual environment.
# --no-dev: Do not install development dependencies.
# --no-interaction, --no-ansi: For non-interactive CI/CD environments.
RUN poetry config virtualenvs.in-project true && \
    poetry install --no-dev --no-interaction --no-ansi


# --- Stage 2: Final Image ---
# Use a minimal, secure base image.
FROM python:3.11-slim-bookworm

# Set working directory
WORKDIR /app

# Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE 1
# Ensure Python output is sent straight to the terminal without buffering
ENV PYTHONUNBUFFERED 1

# NFR-4.1: Create a non-root user and group
RUN groupadd -r appgroup && useradd --no-log-init -r -g appgroup appuser
RUN chown -R appuser:appgroup /app

# Copy the virtual environment with dependencies from the builder stage
COPY --from=builder /app/.venv ./.venv
# Copy the application source code
COPY ./calculator ./calculator

# Activate the virtual environment
ENV PATH="/app/.venv/bin:$PATH"

# Switch to the non-root user
USER appuser

# Expose the port the API will run on
EXPOSE 8000

# Set the entrypoint for the container.
# This runs the API using the script defined in pyproject.toml.
CMD ["calculator-api"]
