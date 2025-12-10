from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import timedelta

from app.core.database import get_db
from app.core.config import settings
from app.models import User
from app.schemas.user import (
    UserCreate, 
    UserLogin, 
    UserResponse, 
    Token, 
    PasswordResetRequest, 
    PasswordReset
)
from app.services.auth_service import (
    get_password_hash,
    authenticate_user,
    create_access_token,
    get_current_user_email,
    create_password_reset_token,
    verify_password_reset_token
)


from app.services.email_service import EmailService

router = APIRouter(prefix="/auth", tags=["Authentication"])

bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Dependency to get current authenticated user"""
    email = get_current_user_email(credentials.credentials)
    
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.email == email).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data.password)
    
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        hashed_password=hashed_password,
        company_name=user_data.company_name,
        cnpj=user_data.cnpj    
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@router.post("/login", response_model=Token)
def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """Login and get access token"""
    user = authenticate_user(db, login_data.email, login_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(current_user: User = Depends(get_current_user)):
    """Logout user (client-side token removal)"""
    return {
        "message": "Successfully logged out",
        "user": current_user.email
    }

@router.post("/forgot-password")
def forgot_password(
    request: PasswordResetRequest,
    db: Session = Depends(get_db)
):
    """Request password reset"""
    user = db.query(User).filter(User.email == request.email).first()
    
    # Sempre retorna sucesso por segurança (não revela se email existe)
    if not user:
        return {"message": "If the email exists, a password reset link has been sent"}
    
    # Create reset token
    reset_token = create_password_reset_token(user.email)
    
    # Send email
    email_sent = EmailService.send_password_reset_email(user.email, reset_token)
    
    if not email_sent:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error sending email. Please try again later."
        )
    
    return {"message": "If the email exists, a password reset link has been sent"}


@router.post("/reset-password")
def reset_password(
    request: PasswordReset,
    db: Session = Depends(get_db)
):
    """Reset password with token"""
    email = verify_password_reset_token(request.token)
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )
    
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Update password
    user.hashed_password = get_password_hash(request.new_password)
    db.commit()
    
    return {"message": "Password successfully reset"}