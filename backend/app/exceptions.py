import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class AppException(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail


class NotFoundError(AppException):
    def __init__(self, detail: str = "资源不存在"):
        super().__init__(404, detail)


class AuthError(AppException):
    def __init__(self, detail: str = "认证失败"):
        super().__init__(401, detail)


class ForbiddenError(AppException):
    def __init__(self, detail: str = "权限不足"):
        super().__init__(403, detail)


class BusinessError(AppException):
    def __init__(self, detail: str):
        super().__init__(400, detail)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        logger.warning("AppException: %s %s", exc.status_code, exc.detail)
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("未处理异常: %s", exc)
        return JSONResponse(status_code=500, content={"detail": "服务器内部错误"})