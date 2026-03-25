from typing import Dict

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings
from app.core.exceptions import AppException


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/login")


async def get_current_user_payload(token: str = Depends(oauth2_scheme)) -> Dict:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email = payload.get("email")
        if email is None:
            raise AppException(status_code=401, detail="Could not validate credentials")
        return payload
    except jwt.PyJWTError as exc:
        raise AppException(status_code=401, detail="Could not validate credentials") from exc


async def require_any_authenticated(
    payload: Dict = Depends(get_current_user_payload),
) -> Dict:
    return payload
