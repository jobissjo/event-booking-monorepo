from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from typing import Dict
import jwt

from app.core.config import settings
from app.core.exceptions import AppException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")


async def get_current_user_payload(token: str = Depends(oauth2_scheme)) -> Dict:
    """
    Decodes the JWT and returns the payload dict.
    Expected payload fields: 'email', 'role'
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("email")
        if email is None:
            raise AppException(status_code=401, detail="Could not validate credentials")
        return payload
    except jwt.PyJWTError:
        raise AppException(status_code=401, detail="Could not validate credentials")


async def require_organizer_or_admin(
    payload: Dict = Depends(get_current_user_payload),
) -> Dict:
    """
    Allows access only for users with role 'organizer' or 'admin'.
    """
    role: str = payload.get("role", "")
    if role not in ("organizer", "admin"):
        raise AppException(
            status_code=403,
            detail="Only organizers or admins can perform this action",
        )
    return payload


async def require_any_authenticated(
    payload: Dict = Depends(get_current_user_payload),
) -> Dict:
    """
    Allows any authenticated user (user, organizer, admin).
    """
    return payload
