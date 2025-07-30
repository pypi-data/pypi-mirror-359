"""Main module for the ZMP AIops Pilot."""

import logging
import logging.config
import secrets
import time
from contextlib import asynccontextmanager
from http import HTTPStatus

import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from motor.motor_asyncio import AsyncIOMotorClient
from starlette.middleware.base import _StreamingResponse
from starlette.middleware.sessions import SessionMiddleware
from starlette_csrf import CSRFMiddleware
from zmp_authentication_provider.routes.auth import router as auth_router
from zmp_authentication_provider.service.auth_service import AuthService

from axmp_ai_agent_studio.exception.servivce_exception import StudioBackendException
from axmp_ai_agent_studio.router import agent_profile_router, healthy_router
from axmp_ai_agent_studio.scheme.response_model import ResponseModel, Result
from axmp_ai_agent_studio.service.agent_service import AgentService
from axmp_ai_agent_studio.setting import (
    application_settings,
    mongodb_settings,
)

logger = logging.getLogger("appLogger")

server = [
    {"url": "https://studio.ags.cloudzcp.net", "description": "Staging Server"},
    {"url": "https://studio.dev.cloudzcp.net", "description": "Dev Server"},
    {"url": "http://localhost:7000", "description": "Local Server"},
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan for the FastAPI app."""
    try:
        # 1. Initialize MongoDB Connection
        mongodb_client: AsyncIOMotorClient = AsyncIOMotorClient(
            mongodb_settings.uri,
            serverSelectionTimeoutMS=mongodb_settings.connection_timeout_ms,
            heartbeatFrequencyMS=3600000,
            tz_aware=True,
        )
        database = mongodb_client[mongodb_settings.database]
        logger.info("MongoDB initialized")

        # 2. Initialize Auth Service
        app.state.auth_service = await AuthService.initialize(database=database)
        logger.info("Auth Service initialized")

        # 3. Initialize Agent Service
        app.state.agent_service = await AgentService.initialize(database=database)
        logger.info("Agent Service initialized")

        yield

    finally:
        # 1. Close MongoDB Connection
        if mongodb_client:
            mongodb_client.close()
        logger.info("MongoDB connection closed")


app = FastAPI(
    # root_path=f"{application_settings.root_path}",
    title=f"{application_settings.title}",
    description=f"{application_settings.description}",
    version=f"{application_settings.version}",
    docs_url=f"{application_settings.docs_url}",
    openapi_url=f"{application_settings.openapi_url}",
    redoc_url=f"{application_settings.redoc_url}",
    default_response_class=JSONResponse,
    debug=True,
    # servers=server,
    root_path_in_servers=True,
    lifespan=lifespan,
)

app.mount(
    f"{application_settings.root_path}/html",
    StaticFiles(directory="public/html"),
    name="html",
)


# downgrading the openapi version to 3.0.0
def custom_openapi():
    """Downgrade the openapi version to 3.0.0."""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        openapi_version="3.0.0",
        servers=app.servers,
    )
    app.openapi_schema = openapi_schema

    return app.openapi_schema


# TODO: uncomment this if needed to integrate with zmp-api-gateway
# app.openapi = custom_openapi

# include routers here
app.include_router(auth_router, tags=["auth"], prefix=application_settings.root_path)
# agent profile router
app.include_router(
    agent_profile_router, tags=["agent_profile"], prefix=application_settings.root_path
)
# TODO: add more routers here with tags and prefix
app.include_router(healthy_router, tags=["healthy"])

# add cors middleware here
app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# add csrf middleware here
__csrf_secret_key = secrets.token_urlsafe(16)
logger.info(f"CRSF Secret Key: {__csrf_secret_key}")
# references
# https://pypi.org/project/starlette-csrf/3.0.0/
# https://dev-in-seoul.tistory.com/44#CORS%20%EC%84%A4%EC%A0%95%EA%B3%BC%20CSRF%20%EA%B3%B5%EA%B2%A9%EC%9D%84%20%EB%A7%89%EA%B8%B0-1
app.add_middleware(
    CSRFMiddleware,
    secret=__csrf_secret_key,
    cookie_domain="localhost",
    cookie_name="csrftoken",
    cookie_path="/",
    cookie_secure=False,
    cookie_httponly=True,
    cookie_samesite="lax",
    header_name="x-csrf-token",
    safe_methods={"GET", "HEAD", "OPTIONS", "TRACE", "POST", "PUT", "DELETE", "PATCH"},
)

# add session middleware here
__session_secret_key = secrets.token_urlsafe(32)
logger.info(f"Session Secret Key: {__session_secret_key}")

app.add_middleware(
    SessionMiddleware,
    secret_key=__session_secret_key,
    session_cookie="session_id",
    max_age=1800,
    same_site="lax",
    https_only=False,  # TODO: change to True
)


@app.middleware("http")
async def http_middleware(request: Request, call_next):
    """HTTP Middleware to add custom headers to the response.

    1. Display request information
    2. Put process time information into Header: X-Process-Time
    3. Display response information
    """
    await __display_request_info(request)

    start_time = time.time()

    response = await call_next(request)

    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.5f}"

    logger.info(
        f"Process time:{process_time:.5f} - URL: {request.url} - Proceeded successfully!"
    )

    await __display_response_info(response)

    return response


@app.exception_handler(StudioBackendException)
async def exception_handler(request: Request, e: StudioBackendException):
    """Exception handler for StudioBackendException."""
    return JSONResponse(
        status_code=e.status_code,
        content=ResponseModel(
            result=Result.FAILED, code=e.code, message=e.detail
        ).model_dump(exclude_none=True),
    )


async def __display_request_info(request: Request):
    """Display request information."""
    line = "=" * 10
    request_info = "\n"
    request_info += line + " REQUEST Started " + line + "\n"
    request_info += f"# Headers: {dict(request.headers)}\n"

    request_info += f"# Path: {request.url.path}\n"
    request_info += f"# Method: {request.method}\n"

    body = await request.body()
    request_info += f"# Body: {body.decode()}\n"

    request_info += f"# Query Params: {dict(request.query_params)}\n"
    request_info += line + " REQUEST Finished " + line + "\n"

    logger.info(request_info)


async def __display_response_info(response: Response):
    """Display response information."""
    line = "=" * 10
    response_info = "\n"
    response_info += line + " RESPONSE Started " + line + "\n"
    response_info += f"# Headers: {dict(response.headers)}\n"
    response_info += f"# Status Code: {response.status_code}\n"

    if isinstance(response, _StreamingResponse):
        original_iterator = response.body_iterator

        async def __log_and_stream_response(buffer: str):
            response_body = b""
            async for chunk in original_iterator:
                response_body += chunk
                yield chunk
            buffer += f"# Body: {response_body.decode('utf-8')}\n"
            buffer += line + " RESPONSE Finished " + line + "\n"
            if response.status_code >= HTTPStatus.BAD_REQUEST:
                logger.error(buffer)
            else:
                logger.info(buffer)

        response.body_iterator = __log_and_stream_response(response_info)
    else:
        response_info += f"# Body: {response.body}\n"
        response_info += line + " RESPONSE Finished " + line + "\n"
        logger.info(response_info)


if __name__ == "__main__":
    uvicorn.run(
        app="axmp_ai_agent_studio.main:app",
        host="0.0.0.0",
        reload=False,
        port=7700,
        workers=1,
    )
