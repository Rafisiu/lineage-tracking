from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from services.keycloak_service import keycloak_service

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

class LoginRequest(BaseModel):
    username: str
    password: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class LogoutRequest(BaseModel):
    refresh_token: str

@router.post("/login")
async def login(request: LoginRequest):
    """
    Login with Keycloak using username/email and password
    """
    if not request.username or not request.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username and password are required"
        )
    
    result = keycloak_service.authenticate(request.username, request.password)
    
    if result.get('success'):
        return {
            "success": True,
            "data": {
                "access_token": result['access_token'],
                "refresh_token": result.get('refresh_token'),
                "expires_in": result.get('expires_in'),
                "token_type": result.get('token_type'),
                "user": result.get('user')
            }
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result.get('error', 'Invalid credentials')
        )

@router.post("/refresh")
async def refresh_token(request: RefreshTokenRequest):
    """
    Refresh access token using refresh token
    """
    if not request.refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token is required"
        )
    
    result = keycloak_service.refresh_token(request.refresh_token)
    
    if result.get('success'):
        return {
            "success": True,
            "data": {
                "access_token": result['access_token'],
                "refresh_token": result.get('refresh_token'),
                "expires_in": result.get('expires_in'),
                "token_type": result.get('token_type')
            }
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result.get('error', 'Failed to refresh token')
        )

@router.post("/logout")
async def logout(request: LogoutRequest):
    """
    Logout user by invalidating refresh token
    """
    if not request.refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token is required"
        )
    
    success = keycloak_service.logout(request.refresh_token)
    
    if success:
        return {
            "success": True,
            "message": "Logged out successfully"
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )

@router.get("/me")
async def get_current_user(authorization: str = None):
    """
    Get current user info from access token
    """
    if not authorization or not authorization.startswith('Bearer '):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing authorization header"
        )
    
    access_token = authorization.replace('Bearer ', '')
    user_info = keycloak_service.get_user_info(access_token)
    
    if user_info:
        return {
            "success": True,
            "data": user_info
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
