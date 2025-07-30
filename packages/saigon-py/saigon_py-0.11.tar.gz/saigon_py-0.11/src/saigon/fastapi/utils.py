import logging
from datetime import datetime
from contextvars import ContextVar
from typing import Annotated, Optional, Self

from pydantic import ConfigDict, Field, ValidationError

from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import (
    FastAPI, Query, Header, BackgroundTasks, Depends, status, Request, APIRouter
)
from fastapi.routing import APIRoute
from fastapi.responses import JSONResponse

from ..model import QueryDataParams, QueryDataPaginationToken
from ..logutils import asynclogcontext
from ..model import TimeRange

from .headers import *
from .handlers import EmptyResponseBody

__all__ = [
    'use_route_names_as_operation_ids',
    'LogMiddleware',
    'AppContext',
    'AppContextDependency',
    'app_context',
    'validate_query_pagination_params',
    'validate_query_date_range',
    'validation_error_exception_handler',
    'create_app'
]

_APP_CONTEXT = ContextVar('_APP_CONTEXT')


def use_route_names_as_operation_ids(app: FastAPI) -> None:
    """
    Simplify operation IDs so that generated API clients have simpler function
    names.

    Should be called only after all routes have been added.
    """
    for route in app.routes:
        if isinstance(route, APIRoute):
            route.operation_id = route.name  # in this case, 'read_items'


def validate_query_pagination_params(
        query_id: Annotated[str, Query(alias='QueryId')] = None,
        next_token: Annotated[str, Query(alias='NextToken')] = None,
        max_frame_count: Annotated[int, Query(alias='MaxCount', gt=0)] = None
) -> QueryDataParams:
    return QueryDataParams(
        max_count=max_frame_count,
        query=QueryDataPaginationToken(
            query_id=query_id,
            next_token=next_token
        ) if query_id and next_token else None
    )


def validate_query_date_range(
        start_time: Annotated[datetime, Query(alias='StartTime')] = None,
        end_time: Annotated[datetime, Query(alias='EndTime')] = None
) -> TimeRange | None:
    if start_time is None and end_time is None:
        return None

    if end_time is None:
        end_time = datetime.now()

    if start_time is None:
        start_time = datetime(
            year=1, month=1, day=1, hour=0, minute=0, microsecond=0
        )

    return TimeRange(
        start=start_time, end=end_time
    )


def validation_error_exception_handler(
        _: Request, exc: Exception
) -> JSONResponse:
    """
    Custom exception handler for Pydantic's ValidationError.
    This ensures that ValidationErrors raised manually (e.g., from Depends functions)
    return a 422 Unprocessable Entity response with structured error details,
    consistent with FastAPI's default Pydantic error responses.
    """
    # The 'errors()' method of ValidationError returns a list of dictionaries,
    # which is the standard format for FastAPI's 422 responses.
    if isinstance(exc, ValidationError):
        # The 'errors()' method of ValidationError returns a list of dictionaries,
        # which is the standard format for FastAPI's 422 responses.
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": exc.errors()},
        )
    else:
        # If it's not a ValidationError, re-raise or handle as a generic 500 error.
        # For simplicity, we'll return a generic 500 here.
        # In a real app, you might want to log the unexpected exception.
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": f"{exc}"},
        )


class LogMiddleware(BaseHTTPMiddleware):
    """
    Middleware implementation for ``fastapi`` that provides two additions:
    - Wraps ``dispatch`` with ``asynclogcontext`` so that a log context is available for
      all endpoints implementations
    - Encloses the ``call_next`` call under two log messages indicating the reception and return
      of a request and response, respectively.

      You can simply add this middleware to the ``fastapi`` app::

        app.add_middleware(LogMiddleware, logger=logger)
    """

    def __init__(self, app, logger: logging.Logger):
        super().__init__(app)
        self._logger = logger

    async def dispatch(self, request, call_next):
        async with asynclogcontext() as alc:
            if request_id := request.headers.get(AWS_API_REQUEST_ID_HEADER_NAME, None):
                alc.set(request_id=request_id)
            if identity_id := request.headers.get(AWS_COGNITO_IAM_AUTH_PROVIDER_HEADER_NAME):
                alc.set(caller_id=identity_id)

            self._logger.info(
                'Received request',
                extra=dict(
                    method=request.method,
                    url=str(request.url)
                )
            )

            response = await call_next(request)

            self._logger.info(
                'Return response',
                extra=dict(status_code=response.status_code)
            )

            return response


class AppContext(RequestContext):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    background_tasks: Optional[BackgroundTasks] = Field(None, exclude=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    async def from_route(
            cls,
            background_tasks: BackgroundTasks,
            request_context: Annotated[RequestContext, Header()]
    ) -> Self:
        _APP_CONTEXT.set(
            context := AppContext(
                background_tasks=background_tasks,
                **request_context.model_dump(by_alias=False)
            )
        )
        return context


AppContextDependency = Depends(AppContext.from_route)


def app_context() -> AppContext:
    return _APP_CONTEXT.get()


def create_app(
        api_router: APIRouter,
        logger: logging.Logger,
        root_path: Optional[str] = '/v1',
        health_path: Optional[str | None] = '/',
        **kwargs
) -> FastAPI:
    app = FastAPI(
        root_path=root_path, **kwargs
    )
    app.add_middleware(LogMiddleware, logger=logger)
    app.add_exception_handler(ValidationError, validation_error_exception_handler)
    app.include_router(api_router, dependencies=[AppContextDependency])
    if health_path:
        app.add_api_route(health_path, lambda: EmptyResponseBody())

    use_route_names_as_operation_ids(app)

    return app
