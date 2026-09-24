import base64, hashlib, hmac, json, secrets, time
from fastapi import HTTPException, Request, status
from src.config import get_settings

COOKIE_NAME = "echomind_session"

def _sign(payload: bytes, secret: str) -> str:
    return hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()

def create_session(username: str) -> str:
    settings = get_settings()
    if not settings.auth_session_secret:
        raise RuntimeError("Authentication is not configured")
    payload = json.dumps({"sub": username, "exp": int(time.time()) + settings.auth_session_ttl_seconds}, separators=(",", ":")).encode()
    encoded = base64.urlsafe_b64encode(payload).decode().rstrip("=")
    return f"{encoded}.{_sign(payload, settings.auth_session_secret)}"

def require_authenticated(request: Request) -> str:
    settings = get_settings()
    token = request.cookies.get(COOKIE_NAME)
    if not settings.auth_username or not settings.auth_password or not settings.auth_session_secret:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Authentication is not configured")
    if not token or "." not in token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")
    encoded, signature = token.rsplit(".", 1)
    try:
        payload = base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4))
        data = json.loads(payload)
    except (ValueError, json.JSONDecodeError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session") from None
    if not hmac.compare_digest(_sign(payload, settings.auth_session_secret), signature) or data.get("sub") != settings.auth_username or data.get("exp", 0) < time.time():
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")
    return settings.auth_username

def valid_credentials(username: str, password: str) -> bool:
    settings = get_settings()
    return bool(settings.auth_username and settings.auth_password and secrets.compare_digest(username, settings.auth_username) and secrets.compare_digest(password, settings.auth_password))
