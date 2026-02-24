# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

from typing import Dict, Any
from app.services.payment.base import PaymentProvider, PaymentProviderError
from app.services.payment.mock import MockPaymentProvider
from app.core.config import settings


class PaymentFactory:
    """
    Factory class for creating payment providers
    
    Usage:
        provider = PaymentFactory.create('payplug')
        result = await provider.create_payment(...)
    """
    
    @staticmethod
    def create(provider_name: str, config: Dict[str, Any] = None) -> PaymentProvider:
        """
        Create a payment provider instance
        
        Args:
            provider_name: Provider name ('payplug', 'floa', 'findomestic', 'mock')
            config: Optional configuration dict. If None, uses settings.
        
        Returns:
            PaymentProvider instance
        
        Raises:
            ValueError: If provider name is invalid
        """
        
        # Use default config from settings if not provided
        if config is None:
            config = PaymentFactory._get_default_config(provider_name)
        
        # Create provider instance
        if provider_name == 'mock':
            return MockPaymentProvider(config)
        
        elif provider_name == 'payplug':
            # For now, return mock until real implementation is ready
            # When ready, uncomment:
            # from app.services.payment.payplug import PayplugProvider
            # return PayplugProvider(config)
            return MockPaymentProvider(config)
        
        elif provider_name == 'floa':
            # For now, return mock until real implementation is ready
            # When ready, uncomment:
            # from app.services.payment.floa import FloaProvider
            # return FloaProvider(config)
            return MockPaymentProvider(config)
        
        elif provider_name == 'findomestic':
            # For now, return mock until real implementation is ready
            # When ready, uncomment:
            # from app.services.payment.findomestic import FindomesticProvider
            # return FindomesticProvider(config)
            return MockPaymentProvider(config)
        
        else:
            raise ValueError(f"Unknown payment provider: {provider_name}")
    
    @staticmethod
    def _get_default_config(provider_name: str) -> Dict[str, Any]:
        """
        Get default configuration for a provider from settings
        
        Args:
            provider_name: Provider name
        
        Returns:
            Configuration dict
        """
        
        # Default test configuration
        base_config = {
            'environment': 'test',
            'webhook_secret': 'test_webhook_secret'
        }
        
        # Provider-specific configs
        if provider_name == 'payplug':
            base_config.update({
                'api_key': getattr(settings, 'PAYPLUG_API_KEY', 'test_key'),
                'publishable_key': getattr(settings, 'PAYPLUG_PUBLISHABLE_KEY', 'test_pub_key'),
            })
        
        elif provider_name == 'floa':
            base_config.update({
                'api_key': getattr(settings, 'FLOA_API_KEY', 'test_key'),
                'api_secret': getattr(settings, 'FLOA_API_SECRET', 'test_secret'),
                'merchant_id': getattr(settings, 'FLOA_MERCHANT_ID', 'test_merchant'),
            })
        
        elif provider_name == 'findomestic':
            base_config.update({
                'api_key': getattr(settings, 'FINDOMESTIC_API_KEY', 'test_key'),
                'api_secret': getattr(settings, 'FINDOMESTIC_API_SECRET', 'test_secret'),
            })
        
        return base_config


# Export main classes
__all__ = [
    'PaymentProvider',
    'PaymentProviderError',
    'MockPaymentProvider',
    'PaymentFactory'
]
