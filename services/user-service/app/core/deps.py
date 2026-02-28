from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.database import get_db
from app.core.exceptions import AppException
from app.repository.user import UserRepository
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/users/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("email")
        if email is None:
            raise AppException(status_code=401, detail="Could not validate credentials")
    except jwt.PyJWTError:
        raise AppException(status_code=401, detail="Could not validate credentials")
        
    user_repo = UserRepository(db)
    user = await user_repo.get_user_by_email(email=email)
    if user is None:
        raise AppException(status_code=401, detail="User not found")
        
    if not user.is_active:
        raise AppException(status_code=400, detail="Inactive user")
        
    return user
