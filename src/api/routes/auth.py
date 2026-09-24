from typing import Annotated
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, Response, status
from src.auth.session import COOKIE_NAME, create_session, require_authenticated, valid_credentials
from src.config import get_settings

router = APIRouter(prefix="/auth", tags=["auth"])
class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
def login(request: LoginRequest, response: Response) -> dict[str, str]:
    settings = get_settings()
    if not settings.auth_username or not settings.auth_password or not settings.auth_session_secret:
        raise HTTPException(status_code=503, detail="Authentication is not configured")
    if not valid_credentials(request.username, request.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    response.set_cookie(COOKIE_NAME, create_session(settings.auth_username), max_age=settings.auth_session_ttl_seconds, httponly=True, secure=settings.auth_cookie_secure, samesite="strict", path="/")
    return {"username": settings.auth_username}

@router.get("/session")
def session(username: Annotated[str, Depends(require_authenticated)]) -> dict[str, str]:
    return {"username": username}

@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(response: Response) -> None:
    response.delete_cookie(COOKIE_NAME, path="/", secure=get_settings().auth_cookie_secure, httponly=True, samesite="strict")
