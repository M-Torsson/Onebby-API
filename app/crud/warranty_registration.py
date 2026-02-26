# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from typing import Optional, List
from datetime import datetime
import json

from app.models.warranty_registration import WarrantyRegistration
from app.schemas.warranty_registration import WarrantyRegistrationCreate


class CRUDWarrantyRegistration:
    """
    CRUD operations for WarrantyRegistration model
    
    Handles all database operations for warranty registrations including:
    - Creating warranty registrations
    - Updating registration status
    - Retrieving registration information
    - Listing user registrations
    """
    
    def create(
        self,
        db: Session,
        *,
        registration_in: WarrantyRegistrationCreate,
        is_test: bool = False
    ) -> WarrantyRegistration:
        """
        Create a new warranty registration record
        
        Args:
            db: Database session
            registration_in: Warranty registration creation schema
            is_test: Whether this is a test mode registration
        
        Returns:
            Created WarrantyRegistration object
        """
        
        registration = WarrantyRegistration(
            order_id=registration_in.order_id,
            product_id=registration_in.product_id,
            warranty_id=registration_in.warranty_id,
            customer_name=registration_in.customer_name,
            customer_lastname=registration_in.customer_lastname,
            customer_email=registration_in.customer_email,
            customer_phone=registration_in.customer_phone,
            product_ean13=registration_in.product_ean13,
            product_name=registration_in.product_name,
            status='pending',
            is_test=is_test
        )
        
        db.add(registration)
        db.commit()
        db.refresh(registration)
        
        return registration
    
    def get(
        self,
        db: Session,
        *,
        id: int
    ) -> Optional[WarrantyRegistration]:
        """
        Get warranty registration by ID
        
        Args:
            db: Database session
            id: Registration ID
        
        Returns:
            WarrantyRegistration object or None
        """
        return db.query(WarrantyRegistration).filter(
            WarrantyRegistration.id == id
        ).first()
    
    def get_by_order(
        self,
        db: Session,
        *,
        order_id: int
    ) -> List[WarrantyRegistration]:
        """
        Get all warranty registrations for an order
        
        Args:
            db: Database session
            order_id: Order ID
        
        Returns:
            List of WarrantyRegistration objects
        """
        return db.query(WarrantyRegistration).filter(
            WarrantyRegistration.order_id == order_id
        ).all()
    
    def get_by_transaction_id(
        self,
        db: Session,
        *,
        transaction_id: str
    ) -> Optional[WarrantyRegistration]:
        """
        Get warranty registration by Garanzia3 transaction ID
        
        Args:
            db: Database session
            transaction_id: Garanzia3 transaction ID
        
        Returns:
            WarrantyRegistration object or None
        """
        return db.query(WarrantyRegistration).filter(
            WarrantyRegistration.g3_transaction_id == transaction_id
        ).first()
    
    def list_user_registrations(
        self,
        db: Session,
        *,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None
    ) -> List[WarrantyRegistration]:
        """
        List warranty registrations for a user
        
        Args:
            db: Database session
            user_id: User ID
            skip: Number of records to skip
            limit: Maximum number of records to return
            status: Filter by status (pending, registered, failed, cancelled)
        
        Returns:
            List of WarrantyRegistration objects
        """
        query = db.query(WarrantyRegistration).join(
            WarrantyRegistration.order
        ).filter(
            WarrantyRegistration.order.has(user_id=user_id)
        )
        
        if status:
            query = query.filter(WarrantyRegistration.status == status)
        
        return query.order_by(
            WarrantyRegistration.created_at.desc()
        ).offset(skip).limit(limit).all()
    
    def update_status(
        self,
        db: Session,
        *,
        id: int,
        status: str,
        g3_transaction_id: Optional[str] = None,
        g3_pin: Optional[str] = None,
        g3_response: Optional[dict] = None,
        error_message: Optional[str] = None,
        error_code: Optional[str] = None
    ) -> Optional[WarrantyRegistration]:
        """
        Update warranty registration status and Garanzia3 data
        
        Args:
            db: Database session
            id: Registration ID
            status: New status (pending, registered, failed, cancelled)
            g3_transaction_id: Garanzia3 transaction ID
            g3_pin: Garanzia3 PIN
            g3_response: Full Garanzia3 response
            error_message: Error message if failed
            error_code: Error code if failed
        
        Returns:
            Updated WarrantyRegistration object or None
        """
        registration = self.get(db, id=id)
        if not registration:
            return None
        
        registration.status = status
        registration.updated_at = datetime.utcnow()
        
        if g3_transaction_id:
            registration.g3_transaction_id = g3_transaction_id
        if g3_pin:
            registration.g3_pin = g3_pin
        if g3_response:
            # Convert dict to JSON string for Text column
            registration.g3_response = json.dumps(g3_response) if isinstance(g3_response, dict) else g3_response
        if error_message:
            registration.error_message = error_message
        if error_code:
            registration.error_code = error_code
        
        # Set timestamp based on status
        if status == 'registered':
            registration.registered_at = datetime.utcnow()
        elif status == 'failed':
            registration.failed_at = datetime.utcnow()
        
        db.commit()
        db.refresh(registration)
        
        return registration
    
    def count_user_registrations(
        self,
        db: Session,
        *,
        user_id: int,
        status: Optional[str] = None
    ) -> int:
        """
        Count warranty registrations for a user
        
        Args:
            db: Database session
            user_id: User ID
            status: Filter by status
        
        Returns:
            Count of registrations
        """
        query = db.query(WarrantyRegistration).join(
            WarrantyRegistration.order
        ).filter(
            WarrantyRegistration.order.has(user_id=user_id)
        )
        
        if status:
            query = query.filter(WarrantyRegistration.status == status)
        
        return query.count()
    
    def list_pending_registrations(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[WarrantyRegistration]:
        """
        List all pending warranty registrations (for admin/retry)
        
        Args:
            db: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List of pending WarrantyRegistration objects
        """
        return db.query(WarrantyRegistration).filter(
            WarrantyRegistration.status == 'pending'
        ).order_by(
            WarrantyRegistration.created_at.desc()
        ).offset(skip).limit(limit).all()


# Global CRUD instance
crud_warranty_registration = CRUDWarrantyRegistration()
