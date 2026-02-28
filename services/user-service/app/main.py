from fastapi import FastAPI
from app.routes.user import router as user_router
from app.core.exceptions import AppException, app_exception_handler
from app.core.config import settings

app = FastAPI(title=settings.PROJECT_NAME)

app.add_exception_handler(AppException, app_exception_handler)

app.include_router(user_router, prefix="/api/users", tags=["Users"])

@app.get("/health")
async def health_check():
    return {"status": "ok"}