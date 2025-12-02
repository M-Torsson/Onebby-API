from pydantic import BaseModel
from datetime import datetime


class HealthResponse(BaseModel):
    status: str
    message: str
    timestamp: datetime
    database: str
