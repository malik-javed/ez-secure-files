from fastapi import APIRouter, HTTPException, Depends, status, Query
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import timedelta
from typing import Optional

from ...core.security import verify_password, get_password_hash, create_access_token, generate_verification_token
from ...core import config
from ...models.user import UserCreate, UserResponse, Token, UserLogin, UserType, TokenData
from ...db.database import add_user, find_user_by_email, find_user_by_username, store_verification_token, verify_token
from ...utils.email import send_verification_email

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        email: str = payload.get("sub")
        user_type: str = payload.get("user_type")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email, user_type=user_type)
    except JWTError:
        raise credentials_exception
    
    user = await find_user_by_email(token_data.email)
    if user is None:
        raise credentials_exception
    
    # Add user_id to user dict for convenience
    user["user_id"] = str(user["_id"])
    return user

async def get_verified_user(user = Depends(get_current_user)):
    if not user.get("is_verified", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please verify your email first."
        )
    return user

async def get_ops_user(user = Depends(get_verified_user)):
    if user.get("user_type") != UserType.OPS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only operations users can perform this action"
        )
    return user

async def get_client_user(user = Depends(get_verified_user)):
    if user.get("user_type") != UserType.CLIENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only client users can perform this action"
        )
    return user

@router.post("/signup")
async def signup(user: UserCreate):
    # Check if user already exists
    if await find_user_by_email(user.email):
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    if await find_user_by_username(user.username):
        raise HTTPException(
            status_code=400,
            detail="Username already taken"
        )
    
    # Create new user data
    hashed_password = get_password_hash(user.password)
    verification_token = generate_verification_token()
    
    user_data = {
        "username": user.username,
        "email": user.email,
        "hashed_password": hashed_password,
        "user_type": UserType.CLIENT,  # Default to CLIENT user type
        "is_verified": False,
        "verification_token": verification_token
    }
    
    # Send verification email first
    email_sent = await send_verification_email(user.email, verification_token)
    
    # In production, we require email to be sent successfully
    # In development mode, we can optionally bypass this requirement
    if not email_sent and not config.BYPASS_EMAIL_VERIFICATION:
        raise HTTPException(
            status_code=500,
            detail="Failed to send verification email. Please try again later."
        )
    
    # If we're in development mode and bypassing email verification, 
    # we'll log this but continue with user creation
    if not email_sent and config.BYPASS_EMAIL_VERIFICATION:
        print("\n=== DEVELOPMENT MODE ===")
        print("WARNING: Email sending failed but BYPASS_EMAIL_VERIFICATION is enabled.")
        print("Creating user anyway. In production, this would fail.")
        print("=== END DEVELOPMENT INFO ===\n")
    
    # Create user if email was sent successfully or we're bypassing verification
    created_user = await add_user(user_data)
    
    # Return only a message
    return {"message": "User registered successfully. Please check your email to verify your account."}

@router.get("/verify")
async def verify_email(email: str = Query(...), token: str = Query(...)):
    if await verify_token(email, token):
        return {"message": "Email verified successfully. You can now log in."}
    raise HTTPException(
        status_code=400,
        detail="Invalid or expired verification token"
    )

@router.post("/resend-verification")
async def resend_verification_email(email: str = Query(...)):
    # Check if user exists
    user = await find_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
    
    # Check if user is already verified
    if user.get("is_verified", False):
        raise HTTPException(
            status_code=400,
            detail="Email is already verified"
        )
    
    # Generate new verification token
    verification_token = generate_verification_token()
    
    # Store the new token
    await store_verification_token(email, verification_token)
    
    # Send verification email
    email_sent = await send_verification_email(email, verification_token)
    
    if not email_sent and not config.BYPASS_EMAIL_VERIFICATION:
        raise HTTPException(
            status_code=500,
            detail="Failed to send verification email. Please try again later."
        )
    
    return {"message": "Verification email has been resent. Please check your inbox."}

async def authenticate_user(email: str, password: str):
    user = await find_user_by_email(email)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    # Check if user is verified
    if not user.get("is_verified", False):
        # We return a special value to indicate unverified user
        return {"error": "not_verified", "email": email}
    return user

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if we got the special unverified user error
    if isinstance(user, dict) and user.get("error") == "not_verified":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please verify your email first.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"], "user_type": user["user_type"]}, 
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin):
    user = await authenticate_user(user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if we got the special unverified user error
    if isinstance(user, dict) and user.get("error") == "not_verified":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please verify your email first.",
        )
    
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"], "user_type": user["user_type"]}, 
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"} 