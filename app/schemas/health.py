# Author: Muthana
# © 2026 Muthana. All rights reserved.
# Unauthorized copying or distribution is prohibited.

from pydantic import BaseModel
from datetime import datetime


class HealthResponse(BaseModel):
    status: str
    message: str
    timestamp: datetime
    database: str
