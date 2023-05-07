"""Main module."""
from app.auth.api import router
from app.auth.exceptions import api_exception_handler
from app.auth.exceptions import ApiException
from app.auth.exceptions import validation_exception_handler
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from config.settings import Settings


def create_app(conf: Settings = None):
    """Create application."""
    app = FastAPI(title="Test proj")
    register_middlewares(app, conf)
    register_routes(app)
    register_handlers(app)
    return app


def register_handlers(app: FastAPI):
    """Register exception handlers."""
    app.exception_handler(ApiException)(api_exception_handler)
    app.exception_handler(RequestValidationError)(validation_exception_handler)
    app.exception_handler(ValidationError)(validation_exception_handler)


def register_middlewares(app: FastAPI, conf: Settings = None):
    """Register middlewares."""
    origins = ["*"]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def register_routes(app: FastAPI):
    """Register routes."""
    app.include_router(router)
