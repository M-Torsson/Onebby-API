# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

"""
PayPlug Payment Gateway Integration

This module handles payment processing with PayPlug.
Supports creating payments and processing webhooks.
"""

import payplug
from typing import Dict, Any, Optional
from decimal import Decimal
from app.core.config import settings
from loguru import logger


class PayPlugService:
    """Service class for PayPlug payment gateway integration"""
    
    def __init__(self):
        """Initialize PayPlug with API key"""
        if settings.PAYPLUG_API_KEY:
            payplug.set_secret_key(settings.PAYPLUG_API_KEY)
            logger.info(f"PayPlug initialized in {settings.PAYPLUG_MODE} mode")
        else:
            logger.warning("PayPlug API key not configured")
    
    def create_payment(
        self,
        amount: Decimal,
        order_id: int,
        customer_email: str,
        customer_first_name: str,
        customer_last_name: str,
        return_url: str,
        cancel_url: str,
        notification_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a payment with PayPlug
        
        Args:
            amount: Payment amount in EUR (will be converted to cents)
            order_id: Order ID for reference
            customer_email: Customer email
            customer_first_name: Customer first name
            customer_last_name: Customer last name
            return_url: URL to redirect after successful payment
            cancel_url: URL to redirect if payment is cancelled
            notification_url: Webhook URL for payment notifications
        
        Returns:
            Dict containing payment information including payment_url
        
        Raises:
            Exception: If payment creation fails
        """
        try:
            # Convert amount to cents (PayPlug requires amount in cents)
            amount_cents = int(amount * 100)
            
            # Prepare payment data
            payment_data = {
                'amount': amount_cents,
                'currency': 'EUR',
                'billing': {
                    'email': customer_email,
                    'first_name': customer_first_name,
                    'last_name': customer_last_name,
                },
                'hosted_payment': {
                    'return_url': return_url,
                    'cancel_url': cancel_url,
                },
                'metadata': {
                    'order_id': str(order_id),
                    'source': 'onebby_api'
                }
            }
            
            # Add notification URL if provided
            if notification_url:
                payment_data['notification_url'] = notification_url
            elif settings.PAYPLUG_WEBHOOK_URL:
                payment_data['notification_url'] = settings.PAYPLUG_WEBHOOK_URL
            
            # Create payment
            payment = payplug.Payment.create(**payment_data)
            
            logger.info(
                f"PayPlug payment created successfully. "
                f"Payment ID: {payment.id}, Order ID: {order_id}, Amount: {amount} EUR"
            )
            
            # Return payment details
            return {
                'payment_id': payment.id,
                'payment_url': payment.hosted_payment.payment_url,
                'return_url': payment.hosted_payment.return_url,
                'cancel_url': payment.hosted_payment.cancel_url,
                'amount': amount,
                'currency': 'EUR',
                'is_paid': payment.is_paid,
                'created_at': payment.created_at
            }
            
        except Exception as e:
            logger.error(f"Failed to create PayPlug payment for order {order_id}: {str(e)}")
            raise Exception(f"Payment creation failed: {str(e)}")
    
    def retrieve_payment(self, payment_id: str) -> Dict[str, Any]:
        """
        Retrieve payment details from PayPlug
        
        Args:
            payment_id: PayPlug payment ID
        
        Returns:
            Dict containing payment details
        
        Raises:
            Exception: If retrieval fails
        """
        try:
            payment = payplug.Payment.retrieve(payment_id)
            
            return {
                'payment_id': payment.id,
                'amount': payment.amount / 100,  # Convert cents to EUR
                'currency': payment.currency,
                'is_paid': payment.is_paid,
                'failure': payment.failure,
                'metadata': payment.metadata,
                'created_at': payment.created_at
            }
            
        except Exception as e:
            logger.error(f"Failed to retrieve PayPlug payment {payment_id}: {str(e)}")
            raise Exception(f"Payment retrieval failed: {str(e)}")
    
    def process_webhook(self, resource_id: str) -> Dict[str, Any]:
        """
        Process PayPlug webhook notification
        
        Args:
            resource_id: Payment ID from webhook
        
        Returns:
            Dict containing processed payment info
        
        Raises:
            Exception: If processing fails
        """
        try:
            # Retrieve payment details
            payment = payplug.Payment.retrieve(resource_id)
            
            # Extract order ID from metadata
            order_id = payment.metadata.get('order_id')
            
            # Determine payment status
            if payment.is_paid:
                status = 'completed'
            elif payment.failure:
                status = 'failed'
            else:
                status = 'pending'
            
            logger.info(
                f"PayPlug webhook processed. "
                f"Payment ID: {payment.id}, Order ID: {order_id}, Status: {status}"
            )
            
            return {
                'payment_id': payment.id,
                'order_id': order_id,
                'status': status,
                'is_paid': payment.is_paid,
                'amount': payment.amount / 100,  # Convert cents to EUR
                'failure_code': payment.failure.code if payment.failure else None,
                'failure_message': payment.failure.message if payment.failure else None,
            }
            
        except Exception as e:
            logger.error(f"Failed to process PayPlug webhook for payment {resource_id}: {str(e)}")
            raise Exception(f"Webhook processing failed: {str(e)}")
    
    def refund_payment(
        self,
        payment_id: str,
        amount: Optional[Decimal] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Refund a payment (full or partial)
        
        Args:
            payment_id: PayPlug payment ID
            amount: Amount to refund (None for full refund)
            metadata: Optional metadata to attach to refund
        
        Returns:
            Dict containing refund details
        
        Raises:
            Exception: If refund fails
        """
        try:
            # Prepare refund data
            refund_data = {}
            
            if amount:
                # Partial refund
                refund_data['amount'] = int(amount * 100)  # Convert to cents
            
            if metadata:
                refund_data['metadata'] = metadata
            
            # Create refund
            payment = payplug.Payment.retrieve(payment_id)
            refund = payplug.Refund.create(payment_id, **refund_data)
            
            logger.info(
                f"PayPlug refund created. "
                f"Refund ID: {refund.id}, Payment ID: {payment_id}"
            )
            
            return {
                'refund_id': refund.id,
                'payment_id': payment_id,
                'amount': refund.amount / 100,  # Convert cents to EUR
                'currency': refund.currency,
                'metadata': refund.metadata,
                'created_at': refund.created_at
            }
            
        except Exception as e:
            logger.error(f"Failed to refund PayPlug payment {payment_id}: {str(e)}")
            raise Exception(f"Refund failed: {str(e)}")


# Create singleton instance
payplug_service = PayPlugService()
