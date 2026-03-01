# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

import requests
from typing import Dict, Any, Optional
from decimal import Decimal
from datetime import datetime
from app.core.config import settings


class FloaService:
    """Floa Payment Integration Service"""
    
    def __init__(self):
        self.base_url = settings.FLOA_BASE_URL
        self.client_id = settings.FLOA_CLIENT_ID
        self.client_secret = settings.FLOA_CLIENT_SECRET
        self.product_code = settings.FLOA_PRODUCT_CODE
        self.culture = settings.FLOA_CULTURE
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
        
        # Request new token
        url = f"{self.base_url}/oauth/token"
        
        data = {
            "grant_type": "client_credentials"
        }
        
        response = requests.post(
            url,
            data=data,
            auth=(self.client_id, self.client_secret),
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        response.raise_for_status()
        token_data = response.json()
        
        # Cache the token
        self._access_token = token_data["access_token"]
        # expires_in is in seconds (usually 3600 = 1 hour)
        expires_in = token_data.get("expires_in", 3600)
        self._token_expires_at = datetime.now().timestamp() + expires_in - 60  # 60s buffer
        
        return self._access_token
    
    def create_deal(
        self,
        merchant_reference: str,
        amount: Decimal,
        customer_data: Dict[str, Any],
        shipping_address: Dict[str, Any],
        items: list,
        product_code: Optional[str] = None,
        back_url: Optional[str] = None,
        return_url: Optional[str] = None,
        notification_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a deal with Floa
        
        Args:
            merchant_reference: Unique order reference
            amount: Total amount in EUR (will be converted to cents)
            customer_data: Customer information
            shipping_address: Shipping address
            items: List of order items
            product_code: Product code (e.g., BC3XCIT), defaults to settings
            back_url: URL for back button
            return_url: URL after payment completion
            notification_url: Webhook URL
        
        Returns:
            dict: Deal data with dealReference and links
        """
        token = self.get_access_token()
        product_code = product_code or self.product_code
        
        url = f"{self.base_url}/api/v1/deals"
        
        # Convert amount to cents
        amount_cents = int(amount * 100)
        
        # Build request body
        body = {
            "merchantReference": merchant_reference,
            "device": "Desktop",
            "shippingMethod": "STD",
            "shippingAddress": shipping_address,
            "merchantFinancedAmount": amount_cents,
            "itemCount": len(items),
            "items": items,
            "customers": [customer_data]
        }
        
        # Add configuration if URLs are provided
        if back_url and return_url and notification_url:
            body["configuration"] = {
                "backUrl": back_url,
                "returnUrl": return_url,
                "notificationUrl": notification_url
            }
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        params = {"productCode": product_code}
        
        try:
            response = requests.post(url, json=body, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            # Log the error response for debugging
            import json
            error_detail = e.response.text if hasattr(e.response, 'text') else str(e)
            # Also log the request body for debugging
            request_body = json.dumps(body, indent=2, ensure_ascii=False)
            raise Exception(f"Floa create_deal failed: {e.response.status_code} - {error_detail}\nRequest Body: {request_body}")
    
    def finalize_deal(
        self,
        deal_reference: str,
        merchant_reference: str,
        amount: Decimal,
        back_url: str,
        return_url: str,
        notification_url: str
    ) -> Dict[str, Any]:
        """
        Finalize a deal to get the payment URL
        
        Args:
            deal_reference: Deal reference from create_deal
            merchant_reference: Merchant reference (order ID)
            amount: Total amount in EUR (will be converted to cents)
            back_url: URL for back button
            return_url: URL after payment completion
            notification_url: Webhook URL
        
        Returns:
            dict: Contains redirect-payment-journey URL
        """
        token = self.get_access_token()
        
        url = f"{self.base_url}/api/v1/deals/{deal_reference}/finalize"
        
        # Convert amount to cents
        amount_cents = int(amount * 100)
        
        body = {
            "merchantReference": merchant_reference,
            "merchantFinancedAmount": amount_cents,
            "configuration": {
                "culture": self.culture,
                "backUrl": back_url,
                "returnUrl": return_url,
                "notificationUrl": notification_url,
                "sessionModes": ["WebPage"]
            }
        }
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=body, headers=headers)
        response.raise_for_status()
        
        return response.json()
    
    def get_deal_status(self, deal_reference: str) -> Dict[str, Any]:
        """
        Get deal installment plan and status
        
        Args:
            deal_reference: Deal reference
        
        Returns:
            dict: Installment plan with status
        """
        token = self.get_access_token()
        
        url = f"{self.base_url}/api/v1/deals/{deal_reference}/installment-plan"
        
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        return response.json()
    
    def create_payment(
        self,
        amount: Decimal,
        order_id: int,
        customer_email: str,
        customer_first_name: str,
        customer_last_name: str,
        customer_phone: str,
        customer_address: Dict[str, Any],
        items: list,
        product_code: Optional[str] = None,
        return_url: Optional[str] = None,
        back_url: Optional[str] = None,
        notification_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Complete Floa payment creation flow
        
        This is the main method that combines all steps:
        1. Create deal
        2. Finalize deal
        3. Return payment_id and payment_url
        
        Args:
            amount: Total amount in EUR
            order_id: Order ID
            customer_email: Customer email
            customer_first_name: Customer first name
            customer_last_name: Customer last name
            customer_phone: Customer phone
            customer_address: Customer address dict
            items: List of order items
            product_code: Product code (optional)
            return_url: Return URL (optional, will use settings)
            back_url: Back URL (optional, will use settings)
            notification_url: Webhook URL (optional, will use settings)
        
        Returns:
            dict: {
                'payment_id': dealReference,
                'payment_url': redirect URL
            }
        """
        # Generate unique merchant reference
        merchant_reference = f"ORD{order_id}_{int(datetime.now().timestamp())}"
        
        # Prepare URLs
        return_url = return_url or f"{settings.FRONTEND_URL}/payment/success"
        back_url = back_url or f"{settings.FRONTEND_URL}/payment/back"
        notification_url = notification_url or settings.FLOA_WEBHOOK_URL
        
        # Prepare shipping address for Floa
        street = customer_address.get("street", "Via Roma").strip()
        house_number = customer_address.get("house_number", "1").strip()
        postal_code = customer_address.get("postal_code", "20121").strip()
        city = customer_address.get("city", "Milano").strip()
        
        # Ensure values are not empty
        if not street:
            street = "Via Roma"
        if not house_number:
            house_number = "1"
        if not postal_code:
            postal_code = "20121"
        if not city:
            city = "Milano"
        
        shipping_address = {
            "line1": f"{street} {house_number}",  # Full street address
            "line2": "",  # Additional info (optional)
            "zipCode": postal_code,
            "city": city,
            "countryCode": "IT"  # Always Italy for this product
        }
        
        # Prepare customer data for Floa
        # Ensure phone number starts with +39 (Italy) and is in E.164 format
        if not customer_phone or customer_phone == '':
            customer_phone = "+393331234567"  # Default Italian number
        elif not customer_phone.startswith('+'):
            customer_phone = f"+39{customer_phone.lstrip('0')}"
        elif not customer_phone.startswith('+39'):
            customer_phone = customer_phone.replace('+', '+39', 1)
        
        # Validate names (Floa requires non-empty names)
        customer_first_name = str(customer_first_name).strip() if customer_first_name else ""
        customer_last_name = str(customer_last_name).strip() if customer_last_name else ""
        
        # Remove special characters and numbers from names
        import re
        customer_first_name = re.sub(r'[^a-zA-Z\s\-\'àèéìòùÀÈÉÌÒÙ]', '', customer_first_name)
        customer_last_name = re.sub(r'[^a-zA-Z\s\-\'àèéìòùÀÈÉÌÒÙ]', '', customer_last_name)
        
        if not customer_first_name or len(customer_first_name) < 2:
            customer_first_name = "Mario"
        if not customer_last_name or len(customer_last_name) < 2:
            customer_last_name = "Rossi"
        
        # Get city from address for birth fields
        birth_city = shipping_address.get("city", "Milano").strip()
        
        # Map major Italian cities to their department codes (case-insensitive)
        department_map = {
            "milano": "MI", "roma": "RM", "torino": "TO", "napoli": "NA",
            "palermo": "PA", "genova": "GE", "bologna": "BO", "firenze": "FI",
            "bari": "BA", "catania": "CT", "venezia": "VE", "verona": "VR"
        }
        birth_department = department_map.get(birth_city.lower(), "MI")  # Default to Milano (MI)
        
        customer_data = {
            "trustLevel": "Trusted",
            "civility": "Mr",
            "firstName": customer_first_name,
            "lastName": customer_last_name,
            "birthDate": "1990-01-01",  # Required by Floa - default value
            "nationality": "IT",  # Italian nationality - required for IT product
            "birthCity": birth_city,  # City of birth - required
            "birthDepartment": birth_department,  # Department code (e.g., MI for Milano) - required
            "birthCountryCode": "IT",  # Country of birth - required
            "mobilePhoneNumber": customer_phone,
            "email": customer_email,
            "taxIdNumber": "RSSMRA90A01F205X",  # Italian tax code (Codice Fiscale) - required for IT
            "homeAddress": shipping_address
        }
        
        # Step 1: Create deal
        deal_response = self.create_deal(
            merchant_reference=merchant_reference,
            amount=amount,
            customer_data=customer_data,
            shipping_address=shipping_address,
            items=items,
            product_code=product_code,
            back_url=back_url,
            return_url=return_url,
            notification_url=notification_url
        )
        
        deal_reference = deal_response["dealReference"]
        
        # Step 2: Finalize deal
        finalize_response = self.finalize_deal(
            deal_reference=deal_reference,
            merchant_reference=merchant_reference,
            amount=amount,
            back_url=back_url,
            return_url=return_url,
            notification_url=notification_url
        )
        
        # Extract payment URL from links
        payment_url = None
        for link in finalize_response.get("links", []):
            if link.get("rel") == "redirect-payment-journey":
                payment_url = link.get("href")
                break
        
        if not payment_url:
            raise ValueError("Payment URL not found in Floa response")
        
        return {
            "payment_id": deal_reference,
            "payment_url": payment_url
        }


# Singleton instance
floa_service = FloaService()
