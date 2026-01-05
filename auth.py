"""
Authentication middleware for Google OAuth.

Verifies Google ID tokens and extracts user information.
"""

from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from google.oauth2 import id_token
from google.auth.transport import requests
from pydantic import BaseModel


# Google OAuth Client ID
GOOGLE_CLIENT_ID = "512560760248-f4tgmruirk6so7fp50bt0sejov9ghvnc.apps.googleusercontent.com"

# HTTP Bearer scheme
security = HTTPBearer(auto_error=False)


class AuthenticatedUser(BaseModel):
    """Authenticated user extracted from Google token."""
    user_id: str  # Google's unique user ID (sub)
    email: str
    name: str
    picture: str | None = None


async def verify_google_token(
    credentials: HTTPAuthorizationCredentials | None = Security(security),
) -> AuthenticatedUser:
    """
    Verify Google ID token and return authenticated user.
    
    Raises HTTPException 401 if token is invalid or missing.
    """
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Missing authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    try:
        # Verify the token with Google
        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            GOOGLE_CLIENT_ID,
        )
        
        # Token is valid, extract user info
        return AuthenticatedUser(
            user_id=idinfo["sub"],  # Google's unique user ID
            email=idinfo.get("email", ""),
            name=idinfo.get("name", ""),
            picture=idinfo.get("picture"),
        )
    
    except ValueError as e:
        # Invalid token
        raise HTTPException(
            status_code=401,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(user: AuthenticatedUser = Depends(verify_google_token)) -> AuthenticatedUser:
    """Dependency to get the current authenticated user."""
    return user
