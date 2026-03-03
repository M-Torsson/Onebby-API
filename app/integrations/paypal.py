# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

import requests
from typing import Dict, Any, Optional
from decimal import Decimal
from datetime import datetime
from app.core.config import settings
import base64
import logging

logger = logging.getLogger(__name__)


class PayPalService:
    """PayPal Payment Integration Service"""
    
    def __init__(self):
        self.base_url = settings.PAYPAL_BASE_URL
        self.client_id = settings.PAYPAL_CLIENT_ID
        self.client_secret = settings.PAYPAL_CLIENT_SECRET
        self._access_token = None
        self._token_expires_at = None
    
    def get_access_token(self) -> str:
        """
        Get OAuth access token using client_credentials grant
        Token is cached and reused until it expires
        
        Returns:
            str: Bearer access token
        """
        # Check if we have a valid cached token
        if self._access_token and self._token_expires_at:
            if datetime.now().timestamp() < self._token_expires_at:
                return self._access_token
        
        # Create base64 encoded credentials
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        # Request new token
        url = f"{self.base_url}/v1/oauth2/token"
        
        headers = {
            "Authorization": f"Basic {encoded_credentials}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        data = {
            "grant_type": "client_credentials"
        }
        
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        self._access_token = token_data['access_token']
        
        # Calculate expiration time (subtract 60 seconds for safety)
        expires_in = token_data.get('expires_in', 3600)
        self._token_expires_at = datetime.now().timestamp() + expires_in - 60
        
        return self._access_token
    
    def create_order(
        self,
        amount: Decimal,
        currency: str = "EUR",
        return_url: Optional[str] = None,
        cancel_url: Optional[str] = None,
        reference_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a PayPal order
        
        Args:
            amount: Total amount
            currency: Currency code (EUR, USD, etc.)
            return_url: URL to return after approval
            cancel_url: URL for cancellation
            reference_id: Custom reference ID
        
        Returns:
            dict: Order data with id and approval URL
        """
        token = self.get_access_token()
        
        url = f"{self.base_url}/v2/checkout/orders"
        
        # Build request body
        body = {
            "intent": "CAPTURE",
            "purchase_units": [
                {
                    "reference_id": reference_id or f"ORDER_{int(datetime.now().timestamp())}",
                    "amount": {
                        "currency_code": currency,
                        "value": f"{float(amount):.2f}"
                    }
                }
            ],
            "payment_source": {
                "paypal": {
                    "experience_context": {
                        "payment_method_preference": "IMMEDIATE_PAYMENT_REQUIRED",
                        "brand_name": "Onebby",
                        "locale": "it-IT",
                        "landing_page": "LOGIN",
                        "user_action": "PAY_NOW",
                        "return_url": return_url or f"{settings.FRONTEND_URL}/payment/success",
                        "cancel_url": cancel_url or f"{settings.FRONTEND_URL}/payment/cancel"
                    }
                }
            }
        }
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, json=body, headers=headers)
            response.raise_for_status()
            
            order_data = response.json()
            
            # Extract approval URL
            approval_url = None
            for link in order_data.get('links', []):
                if link.get('rel') == 'payer-action':
                    approval_url = link.get('href')
                    break
            
            return {
                'order_id': order_data['id'],
                'status': order_data['status'],
                'approval_url': approval_url,
                'full_response': order_data
            }
            
        except requests.exceptions.HTTPError as e:
            error_detail = e.response.text if hasattr(e.response, 'text') else str(e)
            logger.error(f"PayPal create_order failed: {e.response.status_code} - {error_detail}")
            raise Exception(f"PayPal create_order failed: {error_detail}")
    
    def capture_order(self, order_id: str) -> Dict[str, Any]:
        """
        Capture payment for an approved order
        
        Args:
            order_id: PayPal order ID
        
        Returns:
            dict: Capture result with status
        """
        token = self.get_access_token()
        
        url = f"{self.base_url}/v2/checkout/orders/{order_id}/capture"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, headers=headers)
            response.raise_for_status()
            
            capture_data = response.json()
            
            return {
                'order_id': capture_data['id'],
                'status': capture_data['status'],
                'full_response': capture_data
            }
            
        except requests.exceptions.HTTPError as e:
            error_detail = e.response.text if hasattr(e.response, 'text') else str(e)
            logger.error(f"PayPal capture_order failed: {e.response.status_code} - {error_detail}")
            raise Exception(f"PayPal capture_order failed: {error_detail}")
    
    def get_order_details(self, order_id: str) -> Dict[str, Any]:
        """
        Get order details
        
        Args:
            order_id: PayPal order ID
        
        Returns:
            dict: Order details
        """
        token = self.get_access_token()
        
        url = f"{self.base_url}/v2/checkout/orders/{order_id}"
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            error_detail = e.response.text if hasattr(e.response, 'text') else str(e)
            logger.error(f"PayPal get_order_details failed: {e.response.status_code} - {error_detail}")
            raise Exception(f"PayPal get_order_details failed: {error_detail}")
    
    def create_payment(
        self,
        amount: Decimal,
        order_id: int,
        customer_email: Optional[str] = None,
        return_url: Optional[str] = None,
        cancel_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Complete PayPal payment creation flow
        
        Args:
            amount: Total amount in EUR
            order_id: Internal order ID
            customer_email: Customer email (optional)
            return_url: Return URL after approval
            cancel_url: Cancel URL
        
        Returns:
            dict: {
                'payment_id': PayPal order ID,
                'payment_url': approval URL
            }
        """
        # Generate unique reference
        reference_id = f"ORD{order_id}_{int(datetime.now().timestamp())}"
        
        # Prepare URLs
        return_url = return_url or f"{settings.FRONTEND_URL}/payment/success"
        cancel_url = cancel_url or f"{settings.FRONTEND_URL}/payment/cancel"
        
        # Create PayPal order
        order_result = self.create_order(
            amount=amount,
            currency="EUR",
            return_url=return_url,
            cancel_url=cancel_url,
            reference_id=reference_id
        )
        
        if not order_result.get('approval_url'):
            raise ValueError("PayPal approval URL not found in response")
        
        return {
            "payment_id": order_result['order_id'],
            "payment_url": order_result['approval_url']
        }


# Singleton instance
paypal_service = PayPalService()
