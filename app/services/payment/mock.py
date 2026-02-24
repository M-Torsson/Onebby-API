# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

from typing import Dict, Any, Optional
from decimal import Decimal
from datetime import datetime
import uuid
import hmac
import hashlib
import json

from app.services.payment.base import PaymentProvider, PaymentProviderError


class MockPaymentProvider(PaymentProvider):
    """
    Mock Payment Provider for testing and development
    
    This provider simulates payment processing without connecting to real APIs.
    Perfect for development, testing, and demos.
    
    Features:
    - Simulates all payment flows (success, failure, cancellation)
    - Generates mock payment URLs
    - Supports webhook simulation
    - No external API calls
    
    Usage:
        provider = MockPaymentProvider(config={'environment': 'test'})
        result = await provider.create_payment(...)
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.provider_name = "mock"
    
    async def create_payment(
        self,
        order_id: int,
        amount: Decimal,
        currency: str,
        payment_method: str,
        customer_info: Dict[str, Any],
        return_url: str,
        cancel_url: str,
        webhook_url: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a mock payment
        
        Returns a mock payment URL that simulates the payment gateway page.
        The frontend can display buttons to simulate success/failure/cancel.
        """
        
        # Generate mock payment ID
        provider_payment_id = f"mock_pay_{uuid.uuid4().hex[:12]}"
        
        # Determine test scenario from metadata
        test_scenario = None
        if metadata:
            test_scenario = metadata.get('test_scenario')
        
        # Generate mock payment URL
        # In a real app, this would point to a test payment page
        payment_url = f"{return_url.split('/checkout')[0]}/mock-payment?id={provider_payment_id}"
        
        # Add scenario to URL if specified
        if test_scenario:
            payment_url += f"&scenario={test_scenario}"
        
        # Build response
        response = {
            'provider_payment_id': provider_payment_id,
            'payment_url': payment_url,
            'status': 'pending',
            'provider': 'mock',
            'payment_method': payment_method,
            'amount': float(amount),
            'currency': currency,
            'created_at': datetime.now().isoformat(),
            'metadata': {
                'order_id': order_id,
                'test_scenario': test_scenario,
                'customer_email': customer_info.get('email'),
                'return_url': return_url,
                'cancel_url': cancel_url,
                'webhook_url': webhook_url
            }
        }
        
        return response
    
    async def get_payment_status(self, provider_payment_id: str) -> Dict[str, Any]:
        """
        Get mock payment status
        
        In mock mode, status is always 'pending' until webhook is called.
        """
        
        return {
            'provider_payment_id': provider_payment_id,
            'status': 'pending',
            'message': 'Mock payment pending. Use webhook simulator to complete payment.'
        }
    
    async def refund_payment(
        self,
        provider_payment_id: str,
        amount: Optional[Decimal] = None,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Simulate refund
        """
        
        # Generate mock refund ID
        refund_id = f"mock_refund_{uuid.uuid4().hex[:12]}"
        
        return {
            'refund_id': refund_id,
            'provider_payment_id': provider_payment_id,
            'refunded_amount': float(amount) if amount else 0.0,
            'status': 'refunded',
            'reason': reason,
            'refunded_at': datetime.now().isoformat()
        }
    
    async def verify_webhook(
        self,
        payload: bytes,
        signature: str,
        headers: Dict[str, str]
    ) -> bool:
        """
        Verify mock webhook signature
        
        For mock webhooks, we use a simple HMAC-SHA256 signature.
        """
        
        # Get webhook secret from config
        webhook_secret = self.config.get('webhook_secret', 'mock_webhook_secret_key')
        
        # Calculate expected signature
        expected_signature = hmac.new(
            webhook_secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        # Compare signatures
        return hmac.compare_digest(signature, expected_signature)
    
    async def parse_webhook(
        self,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Parse mock webhook payload
        
        Mock webhook format:
        {
            "event_type": "payment.completed" | "payment.failed" | "payment.cancelled",
            "payment_id": "mock_pay_...",
            "transaction_id": "mock_txn_...",
            "status": "completed" | "failed" | "cancelled",
            "amount": 1059.90,
            "currency": "EUR",
            "error": {"code": "...", "message": "..."} (if failed),
            "timestamp": "2026-02-24T10:00:00Z"
        }
        """
        
        event_type = payload.get('event_type', 'payment.completed')
        provider_payment_id = payload.get('payment_id')
        status = payload.get('status', 'completed')
        transaction_id = payload.get('transaction_id')
        
        # Normalize to internal format
        normalized = {
            'event_type': event_type,
            'provider_payment_id': provider_payment_id,
            'status': self._normalize_status(status),
            'transaction_id': transaction_id,
            'amount': payload.get('amount'),
            'currency': payload.get('currency', 'EUR'),
            'metadata': {
                'provider': 'mock',
                'raw_status': status
            }
        }
        
        # Add error info if failed
        if 'error' in payload:
            normalized['error'] = payload['error']
        
        return normalized
    
    def _normalize_status(self, provider_status: str) -> str:
        """
        Normalize mock status to internal status
        """
        
        status_map = {
            'pending': 'pending',
            'processing': 'processing',
            'completed': 'completed',
            'success': 'completed',
            'failed': 'failed',
            'failure': 'failed',
            'error': 'failed',
            'cancelled': 'cancelled',
            'canceled': 'cancelled',
            'refunded': 'refunded'
        }
        
        return status_map.get(provider_status.lower(), 'pending')
    
    # ========== Mock-specific helper methods ==========
    
    def generate_mock_webhook_payload(
        self,
        provider_payment_id: str,
        scenario: str = 'success',
        error_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a mock webhook payload for testing
        
        Args:
            provider_payment_id: Payment ID
            scenario: 'success', 'failure', or 'cancelled'
            error_message: Error message if scenario is 'failure'
        
        Returns:
            Mock webhook payload dict
        """
        
        base_payload = {
            'payment_id': provider_payment_id,
            'timestamp': datetime.now().isoformat()
        }
        
        if scenario == 'success':
            base_payload.update({
                'event_type': 'payment.completed',
                'status': 'completed',
                'transaction_id': f"mock_txn_{uuid.uuid4().hex[:12]}",
                'amount': 1059.90,  # Example amount
                'currency': 'EUR'
            })
        
        elif scenario == 'failure':
            base_payload.update({
                'event_type': 'payment.failed',
                'status': 'failed',
                'error': {
                    'code': 'payment_declined',
                    'message': error_message or 'Mock payment declined by bank'
                }
            })
        
        elif scenario == 'cancelled':
            base_payload.update({
                'event_type': 'payment.cancelled',
                'status': 'cancelled'
            })
        
        return base_payload
    
    def generate_webhook_signature(self, payload: bytes) -> str:
        """
        Generate webhook signature for testing
        
        Args:
            payload: Webhook payload as bytes
        
        Returns:
            HMAC-SHA256 signature hex string
        """
        
        webhook_secret = self.config.get('webhook_secret', 'mock_webhook_secret_key')
        
        signature = hmac.new(
            webhook_secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return signature
