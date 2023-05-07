"""Exception module."""
import json

from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse


class ApiException(Exception):
    """Api response exceptions."""

    def __init__(self, status: int, message: str, details: str):
        """Init method."""
        self.status = status
        self.message = message
        self.details = details


class NotFoundException(ApiException):
    """Not found exception."""

    def __init__(self):
        """Init method."""
        super().__init__(status.HTTP_404_NOT_FOUND, 'Resource not found', '')


class AuthenticationException(ApiException):
    """Authentication exception."""

    def __init__(self, message: str = 'Unauthenticated', details: str = ''):
        """Init method."""
        super().__init__(status.HTTP_401_UNAUTHORIZED, message, details)


class PermissionDenied(ApiException):
    """Authentication exception."""

    def __init__(self):
        """Init method."""
        super().__init__(status.HTTP_403_FORBIDDEN, 'Permission denied', '')


class BadRequestException(ApiException):
    """Bad request exception."""

    def __init__(self, message):
        """Init method."""
        super().__init__(status.HTTP_400_BAD_REQUEST, message, '')


class InvalidRefreshToken(ApiException):
    """Refresh token has expired"""

    def __init__(self, message, details=''):
        """Init method."""
        super().__init__(status.HTTP_401_UNAUTHORIZED, message, details)


async def api_exception_handler(request: Request, exc: ApiException):
    """Handle API exceptions."""
    return JSONResponse(
        status_code=exc.status,
        content={"message": exc.message, "details": exc.details},
    )


async def validation_exception_handler(request, exc):
    """Handle validation error"""
    exc_json = json.loads(exc.json())
    response = {"details": [], "message": ''}

    for error in exc_json:
        # Get pydantic error messages and set to response
        response['details'].append({error['loc'][-1]: f": {error['msg']}"})
        response['message'] += error['loc'][-1] + f": {error['msg']} \n "

    return JSONResponse(response, status_code=status.HTTP_400_BAD_REQUEST)
