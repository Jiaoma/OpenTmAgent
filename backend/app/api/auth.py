from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional

from app.models.base import get_db
from app.models import User
from app.schemas import AdminLoginRequest, VisitorLoginRequest, LoginResponse, TokenResponse
from app.config import settings

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=settings.JWT_ACCESS_TOKEN_EXPIRE_HOURS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None


@router.post("/admin-login", response_model=LoginResponse)
async def admin_login(request: AdminLoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.employee_id == request.employee_id).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="非管理员用户")
    
    if not user.password_hash:
        if len(request.password) < settings.ADMIN_PASSWORD_MIN_LENGTH:
            raise HTTPException(status_code=400, detail=f"密码长度至少{settings.ADMIN_PASSWORD_MIN_LENGTH}位")
        user.password_hash = get_password_hash(request.password)
        db.commit()
        access_token = create_access_token(data={"sub": user.employee_id, "is_admin": True})
        return LoginResponse(
            success=True,
            message="首次设置密码成功",
            token=TokenResponse(access_token=access_token, is_admin=True)
        )
    
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="密码错误")
    
    access_token = create_access_token(data={"sub": user.employee_id, "is_admin": True})
    return LoginResponse(
        success=True,
        message="登录成功",
        token=TokenResponse(access_token=access_token, is_admin=True)
    )


@router.post("/visitor-login", response_model=LoginResponse)
async def visitor_login(request: VisitorLoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.employee_id == request.employee_id).first()
    
    if not user:
        user = User(employee_id=request.employee_id, is_admin=False)
        db.add(user)
        db.commit()
        db.refresh(user)
    
    access_token = create_access_token(data={"sub": user.employee_id, "is_admin": False})
    return LoginResponse(
        success=True,
        message="登录成功",
        token=TokenResponse(access_token=access_token, is_admin=False)
    )


@router.get("/me")
async def get_current_user(token: str = None, db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(status_code=401, detail="未提供认证令牌")
    
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="无效的认证令牌")
    
    employee_id = payload.get("sub")
    user = db.query(User).filter(User.employee_id == employee_id).first()
    
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    
    return {
        "id": user.id,
        "employee_id": user.employee_id,
        "is_admin": user.is_admin
    }
