# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.session import get_db
from app.schemas.address import (
    CustomerAddressCreate, CustomerAddressResponse, CustomerAddressUpdate,
    CompanyAddressCreate, CompanyAddressResponse, CompanyAddressUpdate
)
from app.crud import address as crud_address
from app.crud import user as crud_user
from app.core.security.api_key import verify_api_key

router = APIRouter()


# ============= Customer Address Endpoints =============

@router.post("/customers/{customer_id}/addresses", response_model=CustomerAddressResponse, status_code=status.HTTP_201_CREATED)
async def create_customer_address(
    customer_id: int,
    address_data: CustomerAddressCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Create a new address for a customer (requires API Key)
    
    Request Body Example:
    ```json
    {
        "alias": "Home",
        "name": "Dev",
        "last_name": "Test",
        "company": "My Company",
        "address_house_number": "123 Main Street",
        "house_number": "123",
        "city": "Rome",
        "postal_code": "00100",
        "country": "Italy",
        "phone": "+39 123 456 7890"
    }
    ```
    
    All fields are required except:
    - alias (optional)
    - company (optional)
    """
    # Check if customer exists
    customer = crud_user.get_customer_by_id(db, customer_id=customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    # Create address
    address = crud_address.create_customer_address(
        db=db,
        user_id=customer_id,
        address_data=address_data
    )
    
    return address


@router.get("/customers/{customer_id}/addresses", response_model=List[CustomerAddressResponse])
async def get_customer_addresses(
    customer_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Get all addresses for a customer (requires API Key)
    """
    # Check if customer exists
    customer = crud_user.get_customer_by_id(db, customer_id=customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    addresses = crud_address.get_customer_addresses(
        db=db,
        user_id=customer_id,
        skip=skip,
        limit=limit
    )
    
    return addresses


@router.get("/customers/{customer_id}/addresses/{address_id}", response_model=CustomerAddressResponse)
async def get_customer_address(
    customer_id: int,
    address_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Get a specific address for a customer (requires API Key)
    """
    address = crud_address.get_customer_address_by_id(
        db=db,
        address_id=address_id,
        user_id=customer_id
    )
    
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found"
        )
    
    return address


@router.put("/customers/{customer_id}/addresses/{address_id}", response_model=CustomerAddressResponse)
async def update_customer_address(
    customer_id: int,
    address_id: int,
    address_update: CustomerAddressUpdate,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Update a customer address (requires API Key)
    
    Request Body Example:
    ```json
    {
        "alias": "Work",
        "city": "Milan",
        "postal_code": "20100"
    }
    ```
    """
    update_data = address_update.dict(exclude_unset=True)
    
    address = crud_address.update_customer_address(
        db=db,
        address_id=address_id,
        user_id=customer_id,
        update_data=update_data
    )
    
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found"
        )
    
    return address


@router.delete("/customers/{customer_id}/addresses/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer_address(
    customer_id: int,
    address_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Delete a customer address (requires API Key)
    """
    success = crud_address.delete_customer_address(
        db=db,
        address_id=address_id,
        user_id=customer_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found"
        )
    
    return None


# ============= Company Address Endpoints =============

@router.post("/companies/{company_id}/addresses", response_model=CompanyAddressResponse, status_code=status.HTTP_201_CREATED)
async def create_company_address(
    company_id: int,
    address_data: CompanyAddressCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Create a new address for a company (requires API Key)
    
    Request Body Example:
    ```json
    {
        "alias": "Headquarters",
        "company_name": "My Company SRL",
        "address_house_number": "456 Business Ave",
        "house_number": "456",
        "city": "Rome",
        "postal_code": "00100",
        "country": "Italy",
        "phone": "+39 123 456 7890"
    }
    ```
    
    All fields are required except:
    - alias (optional)
    """
    # Check if company exists
    company = crud_user.get_company_by_id(db, company_id=company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    # Create address
    address = crud_address.create_company_address(
        db=db,
        user_id=company_id,
        address_data=address_data
    )
    
    return address


@router.get("/companies/{company_id}/addresses", response_model=List[CompanyAddressResponse])
async def get_company_addresses(
    company_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Get all addresses for a company (requires API Key)
    """
    # Check if company exists
    company = crud_user.get_company_by_id(db, company_id=company_id)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    addresses = crud_address.get_company_addresses(
        db=db,
        user_id=company_id,
        skip=skip,
        limit=limit
    )
    
    return addresses


@router.get("/companies/{company_id}/addresses/{address_id}", response_model=CompanyAddressResponse)
async def get_company_address(
    company_id: int,
    address_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Get a specific address for a company (requires API Key)
    """
    address = crud_address.get_company_address_by_id(
        db=db,
        address_id=address_id,
        user_id=company_id
    )
    
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found"
        )
    
    return address


@router.put("/companies/{company_id}/addresses/{address_id}", response_model=CompanyAddressResponse)
async def update_company_address(
    company_id: int,
    address_id: int,
    address_update: CompanyAddressUpdate,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Update a company address (requires API Key)
    
    Request Body Example:
    ```json
    {
        "alias": "Secondary Office",
        "city": "Milan",
        "postal_code": "20100"
    }
    ```
    """
    update_data = address_update.dict(exclude_unset=True)
    
    address = crud_address.update_company_address(
        db=db,
        address_id=address_id,
        user_id=company_id,
        update_data=update_data
    )
    
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found"
        )
    
    return address


@router.delete("/companies/{company_id}/addresses/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company_address(
    company_id: int,
    address_id: int,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """
    Delete a company address (requires API Key)
    """
    success = crud_address.delete_company_address(
        db=db,
        address_id=address_id,
        user_id=company_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Address not found"
        )
    
    return None
