from typing import Any

import jwt
from robyn import Request

from app.core.config import settings


class AuthError(Exception):
    pass


def _extract_bearer_token(request: Request) -> str:
    authorization = None
    for header_name, header_value in request.headers.items():
        if header_name.lower() == "authorization":
            authorization = header_value
            break

    if not authorization:
        raise AuthError("Missing Authorization header")

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise AuthError("Authorization header must use Bearer token")

    return token


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except jwt.PyJWTError as exc:
        raise AuthError("Could not validate credentials") from exc

    email = payload.get("email")
    if email is None:
        raise AuthError("Could not validate credentials")

    return payload


def require_authenticated_request(request: Request) -> dict[str, Any]:
    token = _extract_bearer_token(request)
    return decode_access_token(token)
