"""
Authentication router: signup, login (token), user self access.
"""

from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from . import models, schemas
from .database import get_db
from .auth_utils import get_password_hash, verify_password, create_access_token, oauth2_scheme
from jose import jwt, JWTError
from typing import Optional
import os

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

# PUBLIC_INTERFACE
@router.post("/signup", summary="Sign up", response_model=schemas.UserResponse)
def signup(user_in: schemas.UserSignup, db: Session = Depends(get_db)):
    """Create a new user account."""
    if db.query(models.User).filter(models.User.email == user_in.email).first():
        raise HTTPException(status_code=409, detail="Email already in use")
    if db.query(models.User).filter(models.User.username == user_in.username).first():
        raise HTTPException(status_code=409, detail="Username already taken")
    user = models.User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# PUBLIC_INTERFACE
@router.post("/token", response_model=schemas.Token, summary="Login and get access token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Authenticate and return access token."""
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token({"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

# Auth dependency for protected endpoints
# PUBLIC_INTERFACE
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> models.User:
    """Retrieve current user object from JWT token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials"
    )
    try:
        payload = jwt.decode(token, os.environ.get("SECRET_KEY", "supersecretkey"), algorithms=["HS256"])
        user_id: Optional[str] = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).get(int(user_id))
    if user is None:
        raise credentials_exception
    return user

# PUBLIC_INTERFACE
@router.get("/me", response_model=schemas.UserResponse, summary="Get current user's info")
def read_users_me(current_user: models.User = Depends(get_current_user)):
    """Get details of the currently authenticated user."""
    return current_user
