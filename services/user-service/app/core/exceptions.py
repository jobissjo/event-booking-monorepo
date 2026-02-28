from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

class AppException(HTTPException):
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)

async def app_exception_handler(request: Request, exc: AppException):
    # Depending on requirements, we can either return a JSONResponse directly
    # or raise HTTPException which is caught by FastAPI's default handler.
    # We will raise HTTPException directly as requested: "raise our excepino with HttpException of fastapi and handle that"
    # Actually wait, if we raise it in a handler, it might cause 500 error if another handler isn't registered,
    # so we return JSONResponse which acts like FastAPI's HTTPException handler.
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )
