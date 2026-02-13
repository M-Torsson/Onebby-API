# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security.auth import get_password_hash, verify_password


def get_user(db: Session, user_id: int) -> Optional[User]:
    """Get user by ID"""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """Get user by email"""
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """Get user by username"""
    return db.query(User).filter(User.username == username).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Get all users with pagination"""
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, user: UserCreate) -> User:
    """Create a new user"""
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        full_name=user.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, user: UserUpdate) -> Optional[User]:
    """Update a user"""
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    update_data = user.dict(exclude_unset=True)
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    """Delete a user"""
    db_user = get_user(db, user_id)
    if not db_user:
        return False
    
    db.delete(db_user)
    db.commit()
    return True


def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
    """Authenticate a user by username or email"""
    # Try to find user by username first
    user = get_user_by_username(db, username)
    
    # If not found, try to find by email
    if not user:
        user = get_user_by_email(db, username)
    
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


# ============= Customer CRUD Functions =============

def create_customer(
    db: Session,
    email: str,
    password: str,
    first_name: str,
    last_name: str,
    title: str,
    reg_type: str = "user"
) -> User:
    """Create a new customer"""
    hashed_password = get_password_hash(password)
    
    # Generate username from email (use email as username for customers)
    username = email.split('@')[0]
    
    # Check if username already exists, if so, add a number suffix
    base_username = username
    counter = 1
    while get_user_by_username(db, username):
        username = f"{base_username}{counter}"
        counter += 1
    
    # Create customer
    db_customer = User(
        reg_type=reg_type,
        title=title,
        first_name=first_name,
        last_name=last_name,
        full_name=f"{first_name} {last_name}",
        email=email,
        username=username,
        hashed_password=hashed_password,
        is_active=True,
        is_superuser=False
    )
    
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer


def authenticate_customer(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate a customer by email"""
    user = get_user_by_email(db, email)
    
    if not user:
        return None
    if user.reg_type != "user":
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def get_customers(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Get all customers with pagination"""
    return db.query(User).filter(User.reg_type == "user").offset(skip).limit(limit).all()


def get_customer_by_id(db: Session, customer_id: int) -> Optional[User]:
    """Get customer by ID"""
    user = db.query(User).filter(User.id == customer_id, User.reg_type == "user").first()
    return user


def update_customer(db: Session, customer_id: int, update_data: dict) -> Optional[User]:
    """Update a customer"""
    db_customer = get_customer_by_id(db, customer_id)
    if not db_customer:
        return None
    
    # Hash password if provided
    if "password" in update_data and update_data["password"]:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    # Update full_name if first_name or last_name changed
    if "first_name" in update_data or "last_name" in update_data:
        first_name = update_data.get("first_name", db_customer.first_name)
        last_name = update_data.get("last_name", db_customer.last_name)
        update_data["full_name"] = f"{first_name} {last_name}"
    
    for field, value in update_data.items():
        if value is not None:  # Only update non-null values
            setattr(db_customer, field, value)
    
    db.commit()
    db.refresh(db_customer)
    return db_customer


def delete_customer(db: Session, customer_id: int) -> bool:
    """Delete a customer"""
    db_customer = get_customer_by_id(db, customer_id)
    if not db_customer:
        return False
    
    db.delete(db_customer)
    db.commit()
    return True


# ============= Company CRUD Functions =============

def create_company(
    db: Session,
    email: str,
    password: str,
    company_name: str,
    vat_number: str,
    sdi_code: str,
    tax_code: Optional[str] = None,
    pec: Optional[str] = None,
    reg_type: str = "company"
) -> User:
    """Create a new company"""
    hashed_password = get_password_hash(password)
    
    # Generate username from company name or email
    username = company_name.lower().replace(" ", "_")[:50]
    if not username:
        username = email.split('@')[0]
    
    # Check if username already exists, if so, add a number suffix
    base_username = username
    counter = 1
    while get_user_by_username(db, username):
        username = f"{base_username}{counter}"
        counter += 1
    
    # Create company
    db_company = User(
        reg_type=reg_type,
        company_name=company_name,
        vat_number=vat_number,
        tax_code=tax_code,
        sdi_code=sdi_code,
        pec=pec,
        email=email,
        username=username,
        hashed_password=hashed_password,
        approval_status="pending",  # Companies start as pending
        is_active=True,
        is_superuser=False
    )
    
    db.add(db_company)
    db.commit()
    db.refresh(db_company)
    return db_company


def authenticate_company(db: Session, email: str, password: str) -> Optional[User]:
    """Authenticate a company by email"""
    user = get_user_by_email(db, email)
    
    if not user:
        return None
    if user.reg_type != "company":
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def get_companies(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """Get all companies with pagination"""
    return db.query(User).filter(User.reg_type == "company").offset(skip).limit(limit).all()


def get_company_by_id(db: Session, company_id: int) -> Optional[User]:
    """Get company by ID"""
    company = db.query(User).filter(User.id == company_id, User.reg_type == "company").first()
    return company


def update_company(db: Session, company_id: int, update_data: dict) -> Optional[User]:
    """Update a company"""
    db_company = get_company_by_id(db, company_id)
    if not db_company:
        return None
    
    # Hash password if provided
    if "password" in update_data and update_data["password"]:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    for field, value in update_data.items():
        if value is not None:  # Only update non-null values
            setattr(db_company, field, value)
    
    db.commit()
    db.refresh(db_company)
    return db_company


def delete_company(db: Session, company_id: int) -> bool:
    """Delete a company"""
    db_company = get_company_by_id(db, company_id)
    if not db_company:
        return False
    
    db.delete(db_company)
    db.commit()
    return True
