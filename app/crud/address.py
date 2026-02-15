# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.address import Address
from app.schemas.address import (
    CustomerAddressCreate, CustomerAddressUpdate,
    CompanyAddressCreate, CompanyAddressUpdate
)


# ============= Customer Address CRUD Functions =============

def create_customer_address(
    db: Session,
    user_id: int,
    address_data: CustomerAddressCreate
) -> Address:
    """Create a new customer address"""
    db_address = Address(
        user_id=user_id,
        address_type="customer",
        alias=address_data.alias,
        name=address_data.name,
        last_name=address_data.last_name,
        company=address_data.company,
        address_house_number=address_data.address_house_number,
        house_number=address_data.house_number,
        city=address_data.city,
        postal_code=address_data.postal_code,
        country=address_data.country,
        phone=address_data.phone
    )
    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    return db_address


def get_customer_addresses(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[Address]:
    """Get all addresses for a customer"""
    return db.query(Address).filter(
        Address.user_id == user_id,
        Address.address_type == "customer"
    ).offset(skip).limit(limit).all()


def get_customer_address_by_id(
    db: Session,
    address_id: int,
    user_id: int
) -> Optional[Address]:
    """Get a specific customer address by ID"""
    return db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == user_id,
        Address.address_type == "customer"
    ).first()


def update_customer_address(
    db: Session,
    address_id: int,
    user_id: int,
    update_data: dict
) -> Optional[Address]:
    """Update a customer address"""
    db_address = get_customer_address_by_id(db, address_id, user_id)
    if not db_address:
        return None
    
    for field, value in update_data.items():
        if value is not None:
            setattr(db_address, field, value)
    
    db.commit()
    db.refresh(db_address)
    return db_address


def delete_customer_address(
    db: Session,
    address_id: int,
    user_id: int
) -> bool:
    """Delete a customer address"""
    db_address = get_customer_address_by_id(db, address_id, user_id)
    if not db_address:
        return False
    
    db.delete(db_address)
    db.commit()
    return True


# ============= Company Address CRUD Functions =============

def create_company_address(
    db: Session,
    user_id: int,
    address_data: CompanyAddressCreate
) -> Address:
    """Create a new company address"""
    db_address = Address(
        user_id=user_id,
        address_type="company",
        alias=address_data.alias,
        company_name=address_data.company_name,
        address_house_number=address_data.address_house_number,
        house_number=address_data.house_number,
        city=address_data.city,
        postal_code=address_data.postal_code,
        country=address_data.country,
        phone=address_data.phone
    )
    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    return db_address


def get_company_addresses(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[Address]:
    """Get all addresses for a company"""
    return db.query(Address).filter(
        Address.user_id == user_id,
        Address.address_type == "company"
    ).offset(skip).limit(limit).all()


def get_company_address_by_id(
    db: Session,
    address_id: int,
    user_id: int
) -> Optional[Address]:
    """Get a specific company address by ID"""
    return db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == user_id,
        Address.address_type == "company"
    ).first()


def update_company_address(
    db: Session,
    address_id: int,
    user_id: int,
    update_data: dict
) -> Optional[Address]:
    """Update a company address"""
    db_address = get_company_address_by_id(db, address_id, user_id)
    if not db_address:
        return None
    
    for field, value in update_data.items():
        if value is not None:
            setattr(db_address, field, value)
    
    db.commit()
    db.refresh(db_address)
    return db_address


def delete_company_address(
    db: Session,
    address_id: int,
    user_id: int
) -> bool:
    """Delete a company address"""
    db_address = get_company_address_by_id(db, address_id, user_id)
    if not db_address:
        return False
    
    db.delete(db_address)
    db.commit()
    return True


# ============= Generic Address Functions =============

def get_all_addresses_for_user(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 100
) -> List[Address]:
    """Get all addresses for a user (both customer and company)"""
    return db.query(Address).filter(
        Address.user_id == user_id
    ).offset(skip).limit(limit).all()


def get_address_by_id(db: Session, address_id: int) -> Optional[Address]:
    """Get any address by ID"""
    return db.query(Address).filter(Address.id == address_id).first()
