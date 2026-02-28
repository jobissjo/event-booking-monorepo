from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import UserCreate, ProfileBase, Token
from app.repository.user import UserRepository
from app.core.security import verify_password, create_access_token, create_refresh_token
from app.core.exceptions import AppException
from datetime import timedelta
from app.core.config import settings

class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def register_user(self, user_create: UserCreate):
        existing_user = await self.user_repo.get_user_by_email(user_create.email)
        if existing_user:
            raise AppException(status_code=400, detail="Email already registered")
        
        # Hashing logic is currently handled in the Repository as per earlier setup. 
        # (Alternatively you can pass the pre-hashed user).
        user = await self.user_repo.create_user(user_create)
        return user

    async def authenticate_user(self, email: str, password: str) -> Token:
        user = await self.user_repo.get_user_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise AppException(status_code=401, detail="Incorrect email or password")
            
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        access_token = create_access_token(
            data={"email": user.email, "role": user.role}, expires_delta=access_token_expires
        )
        refresh_token = create_refresh_token(
            data={"email": user.email, "role": user.role}, expires_delta=refresh_token_expires
        )
        
        return Token(access_token=access_token, refresh_token=refresh_token)

    async def get_user_profile(self, user_id: int):
        user = await self.user_repo.get_user_by_id(user_id)
        if not user:
            raise AppException(status_code=404, detail="User not found")
        return user

    async def update_user_profile(self, user_id: int, profile_data: ProfileBase):
        updated_profile = await self.user_repo.update_profile(user_id, profile_data)
        if not updated_profile:
            raise AppException(status_code=404, detail="Profile not found")
        user = await self.user_repo.get_user_by_id(user_id)
        return user

    async def delete_user(self, user_id: int):
        success = await self.user_repo.delete_user(user_id)
        if not success:
            raise AppException(status_code=404, detail="User not found")
        return {"detail": "User deleted successfully"}
