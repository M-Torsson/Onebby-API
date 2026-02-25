# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

import httpx
import json
from typing import Dict, Optional
from datetime import datetime
from app.core.config import settings


class Garanzia3Service:
    """
    Garanzia3 API Integration Service
    
    Handles communication with Garanzia3 REST API for warranty registration.
    Supports both test and production modes.
    """
    
    def __init__(self):
        self.api_url = settings.GARANZIA3_API_URL
        self.token = settings.GARANZIA3_TOKEN
        self.is_test_mode = settings.GARANZIA3_MODE == "test"
        self.timeout = 30.0
    
    async def register_warranty(
        self,
        ean13: str,
        customer_name: str,
        customer_lastname: str,
        customer_email: str,
        customer_phone: str
    ) -> Dict:
        """
        Register a warranty with Garanzia3
        
        Args:
            ean13: Product EAN13 code
            customer_name: Customer first name
            customer_lastname: Customer last name
            customer_email: Customer email
            customer_phone: Customer phone number
        
        Returns:
            Dict with keys:
                - success: bool
                - transaction: str (G3 transaction ID)
                - pin: str (G3 PIN code)
                - error: str (if failed)
                - raw_response: dict (full response from G3)
        """
        
        # Test mode: return mock data
        if self.is_test_mode:
            return self._mock_registration(ean13, customer_email)
        
        # Production mode: call real API
        try:
            payload = {
                "token": self.token,
                "ean13": ean13,
                "name": customer_name,
                "lastname": customer_lastname,
                "email": customer_email,
                "phone": customer_phone
            }
            
            headers = {
                "Content-Type": "application/json",
                "cache-control": "no-cache"
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.api_url}/api/v_1/contract/new",
                    json=payload,
                    headers=headers
                )
                
                # Parse response
                response_data = response.json()
                
                # Check if successful (200 status)
                if response.status_code == 200 and response_data.get("message") == "OK":
                    data = response_data.get("data", [])[0] if response_data.get("data") else {}
                    
                    return {
                        "success": True,
                        "transaction": data.get("transaction"),
                        "pin": data.get("pin"),
                        "raw_response": response_data
                    }
                
                # Handle errors
                error_code = response_data.get("code", response.status_code)
                error_message = response_data.get("message", "Unknown error")
                
                return {
                    "success": False,
                    "error": error_message,
                    "error_code": str(error_code),
                    "raw_response": response_data
                }
                
        except httpx.TimeoutException:
            return {
                "success": False,
                "error": "Request timeout - Garanzia3 API did not respond in time",
                "error_code": "timeout"
            }
        except httpx.HTTPError as e:
            return {
                "success": False,
                "error": f"HTTP error: {str(e)}",
                "error_code": "http_error"
            }
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": "Invalid JSON response from Garanzia3",
                "error_code": "invalid_json"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Unexpected error: {str(e)}",
                "error_code": "unknown"
            }
    
    def _mock_registration(self, ean13: str, email: str) -> Dict:
        """
        Mock registration for testing
        
        Returns fake transaction ID and PIN without calling real API
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        mock_transaction = f"{timestamp}_G3TEST_{ean13[:8]}"
        mock_pin = f"TEST{timestamp[-10:]}"
        
        return {
            "success": True,
            "transaction": mock_transaction,
            "pin": mock_pin,
            "raw_response": {
                "data": [{
                    "transaction": mock_transaction,
                    "pin": mock_pin
                }],
                "message": "OK (MOCK MODE)"
            }
        }
    
    def validate_ean13(self, ean13: str) -> bool:
        """
        Validate EAN13 format
        
        Args:
            ean13: EAN13 code to validate
        
        Returns:
            bool: True if valid EAN13 format
        """
        if not ean13 or len(ean13) != 13:
            return False
        
        if not ean13.isdigit():
            return False
        
        return True


# Global instance
garanzia3_service = Garanzia3Service()
