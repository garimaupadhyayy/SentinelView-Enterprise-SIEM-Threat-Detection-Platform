from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.security import decode_token
from app.models.user import User, UserRole

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if creds is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing bearer token")

    payload = decode_token(creds.credentials)
    if not payload or payload.get("type") != "access":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token")

    user = db.query(User).filter(User.username == payload.get("sub")).first()
    if not user or not user.is_active:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "User not found or inactive")
    return user


def require_roles(*roles: UserRole):
    """
    Dependency factory implementing RBAC: e.g. Depends(require_roles(UserRole.ADMIN))
    restricts an endpoint to admins only. Analysts/viewers get 403 with a clear message
    rather than a generic 401, since they ARE authenticated -- just not authorized.
    """

    def dependency(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(
                status.HTTP_403_FORBIDDEN,
                f"Role '{user.role.value}' is not permitted to perform this action. "
                f"Requires one of: {[r.value for r in roles]}",
            )
        return user

    return dependency


# Convenience shortcuts used throughout the API layer
require_admin = require_roles(UserRole.ADMIN)
require_analyst_or_admin = require_roles(UserRole.ADMIN, UserRole.ANALYST)
require_any_role = require_roles(UserRole.ADMIN, UserRole.ANALYST, UserRole.VIEWER)
