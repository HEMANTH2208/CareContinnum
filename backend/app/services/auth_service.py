from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.core.security import verify_password, get_password_hash, create_access_token
from app.schemas.user import UserCreate


def authenticate_user(db: Session, email: str, password: str) -> User:
    """Authenticate user with email and password."""
    user = db.query(User).filter(User.email == email).first()
    
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user


def create_user(db: Session, user_data: UserCreate) -> User:
    """Create a new user."""
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if employee_id already exists (if provided)
    if user_data.employee_id:
        existing_employee = db.query(User).filter(User.employee_id == user_data.employee_id).first()
        if existing_employee:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Employee ID already exists"
            )
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        role=user_data.role,
        department=user_data.department,
        employee_id=user_data.employee_id,
        phone=user_data.phone,
        license_number=user_data.license_number,
        specialization=user_data.specialization
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user
