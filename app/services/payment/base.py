# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from decimal import Decimal
from datetime import datetime


class PaymentProvider(ABC):
    """
    Abstract base class for payment providers
    
    All payment providers (Payplug, Floa, Findomestic) inherit from this class.
    This ensures consistent interface across all payment methods.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize payment provider with configuration
        
        Args:
            config: Configuration dictionary containing:
                - api_key: Provider API key
                - api_secret: Provider API secret (if needed)
                - environment: 'test' or 'production'
                - webhook_secret: Secret for webhook validation
                - Any other provider-specific settings
        """
        self.config = config
        self.environment = config.get('environment', 'test')
        self.is_test_mode = self.environment == 'test'
    
    @abstractmethod
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
        Create a payment with the provider
        
        Args:
            order_id: Internal order ID
            amount: Payment amount
            currency: Currency code (EUR)
            payment_method: Payment method specific to provider
            customer_info: Customer information dict
            return_url: URL to redirect after successful payment
            cancel_url: URL to redirect if payment cancelled
            webhook_url: URL for provider to send webhook notifications
            metadata: Additional metadata
        
        Returns:
            Dictionary containing:
                - provider_payment_id: Payment ID from provider
                - payment_url: URL to redirect customer
                - status: Payment status
                - Any other provider-specific data
        
        Raises:
            PaymentProviderError: If payment creation fails
        """
        pass
    
    @abstractmethod
    async def get_payment_status(self, provider_payment_id: str) -> Dict[str, Any]:
        """
        Get current payment status from provider
        
        Args:
            provider_payment_id: Payment ID from provider
        
        Returns:
            Dictionary containing:
                - status: Current payment status
                - provider_transaction_id: Transaction ID (if completed)
                - Any other status information
        
        Raises:
            PaymentProviderError: If status check fails
        """
        pass
    
    @abstractmethod
    async def refund_payment(
        self,
        provider_payment_id: str,
        amount: Optional[Decimal] = None,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Refund a payment
        
        Args:
            provider_payment_id: Payment ID from provider
            amount: Amount to refund (None for full refund)
            reason: Refund reason
        
        Returns:
            Dictionary containing:
                - refund_id: Refund transaction ID
                - refunded_amount: Amount refunded
                - status: Refund status
        
        Raises:
            PaymentProviderError: If refund fails
        """
        pass
    
    @abstractmethod
    async def verify_webhook(
        self,
        payload: bytes,
        signature: str,
        headers: Dict[str, str]
    ) -> bool:
        """
        Verify webhook signature from provider
        
        Args:
            payload: Raw webhook payload
            signature: Signature from provider
            headers: All webhook HTTP headers
        
        Returns:
            True if signature is valid, False otherwise
        """
        pass
    
    @abstractmethod
    async def parse_webhook(
        self,
        payload: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Parse webhook payload into normalized format
        
        Args:
            payload: Webhook payload from provider
        
        Returns:
            Normalized dictionary containing:
                - event_type: Event type (payment.completed, payment.failed, etc.)
                - provider_payment_id: Payment ID
                - status: Payment status
                - transaction_id: Transaction ID (if applicable)
                - metadata: Additional data
        """
        pass
    
    def _normalize_status(self, provider_status: str) -> str:
        """
        Normalize provider-specific status to internal status
        
        Internal statuses:
        - pending: Payment initiated but not yet processing
        - processing: Payment is being processed
        - completed: Payment successful
        - failed: Payment failed
        - cancelled: Payment cancelled by customer
        - refunded: Payment refunded
        
        Args:
            provider_status: Status from provider
        
        Returns:
            Normalized status string
        """
        # This should be overridden by each provider
        # with their specific status mappings
        return provider_status.lower()


class PaymentProviderError(Exception):
    """
    Custom exception for payment provider errors
    
    Attributes:
        message: Error message
        code: Error code (provider-specific)
        provider: Payment provider name
        recoverable: Whether the error is recoverable (can retry)
    """
    
    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        provider: Optional[str] = None,
        recoverable: bool = False
    ):
        self.message = message
        self.code = code
        self.provider = provider
        self.recoverable = recoverable
        super().__init__(self.message)
    
    def __str__(self):
        parts = [f"PaymentProviderError: {self.message}"]
        if self.provider:
            parts.append(f"Provider: {self.provider}")
        if self.code:
            parts.append(f"Code: {self.code}")
        return " | ".join(parts)
