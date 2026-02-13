# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.schemas.user import (
    UserCreate, UserResponse, UserUpdate, LoginRequest, Token,
    CustomerRegisterRequest, CustomerResponse, CustomerLoginRequest,
    CompanyRegisterRequest, CompanyResponse, CompanyLoginRequest,
    CustomerUpdateRequest, CompanyUpdateRequest
)
from app.crud import user as crud_user
from app.core.security.auth import create_access_token
from app.core.security.dependencies import get_current_active_user
from app.core.security.api_key import verify_api_key

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user: UserCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Register a new user (requires API Key)
    """
    # Check if email already exists
    db_user = crud_user.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Check if username already exists
    db_user = crud_user.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    return crud_user.create_user(db=db, user=user)


@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Login and get access token (requires API Key)
    """
    user = crud_user.authenticate_user(db, login_data.username, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    access_token = create_access_token(data={"sub": str(user.id), "username": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: dict = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Get current user information (requires API Key + JWT)
    """
    user_id = int(current_user["id"])
    user = crud_user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


# ============= Customer Registration & Login Endpoints =============

@router.post("/customers/register", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def register_customer(
    customer_data: CustomerRegisterRequest,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Register a new customer (requires API Key)
    
    Request Body:
    ```json
    {
        "reg_type": "user",
        "title": "Sig.",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "password": "securePassword123"
    }
    ```
    """
    # Check if email already exists
    existing_user = crud_user.get_user_by_email(db, email=customer_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create customer
    customer = crud_user.create_customer(
        db=db,
        email=customer_data.email,
        password=customer_data.password,
        first_name=customer_data.first_name,
        last_name=customer_data.last_name,
        title=customer_data.title,
        reg_type=customer_data.reg_type
    )
    
    return customer


@router.post("/customers/login", response_model=Token)
async def login_customer(
    login_data: CustomerLoginRequest,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Customer login and get access token (requires API Key)
    
    Request Body:
    ```json
    {
        "email": "john.doe@example.com",
        "password": "securePassword123"
    }
    ```
    """
    customer = crud_user.authenticate_customer(db, login_data.email, login_data.password)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not customer.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive account"
        )
    
    access_token = create_access_token(
        data={"sub": str(customer.id), "email": customer.email}
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/customers", response_model=List[CustomerResponse])
async def get_all_customers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Get all customers (requires API Key)
    """
    customers = crud_user.get_customers(db, skip=skip, limit=limit)
    return customers


@router.get("/customers/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Get customer by ID (requires API Key)
    """
    customer = crud_user.get_customer_by_id(db, customer_id=customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    return customer


@router.put("/customers/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: int,
    customer_update: CustomerUpdateRequest,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Update customer (requires API Key)
    """
    update_data = customer_update.dict(exclude_unset=True)
    customer = crud_user.update_customer(db, customer_id=customer_id, update_data=update_data)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    return customer


@router.delete("/customers/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Delete customer (requires API Key)
    """
    success = crud_user.delete_customer(db, customer_id=customer_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    return None


# ============= Company Registration & Login Endpoints =============

@router.post("/companies/register", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def register_company(
    company_data: CompanyRegisterRequest,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Register a new company (requires API Key)
    
    Italian companies must provide both tax_code and pec.
    Foreign companies can omit tax_code and pec.
    
    Request Body:
    ```json
    {
        "reg_type": "company",
        "company_name": "My Company SRL",
        "email": "info@company.com",
        "password": "securePassword123",
        "vat_number": "12345678901",
        "tax_code": "ABCDEF12G34H567I",
        "sdi_code": "ABC1234",
        "pec": "company@pec.it"
    }
    ```
    """
    # Check if email already exists
    existing_user = crud_user.get_user_by_email(db, email=company_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate Italian company requirements
    try:
        company_data.validate_italian_company(company_data.dict())
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    # Create company
    company = crud_user.create_company(
        db=db,
        email=company_data.email,
        password=company_data.password,
        company_name=company_data.company_name,
        vat_number=company_data.vat_number,
        sdi_code=company_data.sdi_code,
        tax_code=company_data.tax_code,
        pec=company_data.pec,
        reg_type=company_data.reg_type
    )
    
    return company


@router.post("/companies/login", response_model=Token)
async def login_company(
    login_data: CompanyLoginRequest,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Company login and get access token (requires API Key)
    
    Request Body:
    ```json
    {
        "email": "info@company.com",
        "password": "securePassword123"
    }
    ```
    """
    company = crud_user.authenticate_company(db, login_data.email, login_data.password)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not company.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive account"
        )
    
    access_token = create_access_token(
        data={"sub": str(company.id), "email": company.email}
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/companies", response_model=List[CompanyResponse])
async def get_all_companies(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Get all companies (requires API Key)
    """
    companies = crud_user.get_companies(db, skip=skip, limit=limit)
    return companies


@router.get("/companies/{company_id}", response_model=CompanyResponse)
async def get_company(
    company_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Get company by ID (requires API Key)
    """
    company = crud_user.get_company_by_id(db, company_id=company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    return company


@router.put("/companies/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: int,
    company_update: CompanyUpdateRequest,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Update company (requires API Key)
    
    Admin can update approval_status to approve/reject companies.
    """
    update_data = company_update.dict(exclude_unset=True)
    company = crud_user.update_company(db, company_id=company_id, update_data=update_data)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    return company


@router.delete("/companies/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(
    company_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Delete company (requires API Key)
    """
    success = crud_user.delete_company(db, company_id=company_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    return None


# ============= Generic User Endpoints (Admin Only) =============

@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
    api_key: str = Depends(verify_api_key)
):
    """
    Get all users (requires API Key + JWT)
    """
    users = crud_user.get_users(db, skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
    api_key: str = Depends(verify_api_key)
):
    """
    Get user by ID (requires API Key + JWT)
    """
    user = crud_user.get_user(db, user_id=user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
    api_key: str = Depends(verify_api_key)
):
    """
    Update user (requires API Key + JWT)
    """
    user = crud_user.update_user(db, user_id=user_id, user=user_update)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_active_user),
    api_key: str = Depends(verify_api_key)
):
    """
    Delete user (requires API Key + JWT)
    """
    success = crud_user.delete_user(db, user_id=user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return None
