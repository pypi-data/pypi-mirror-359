"""App and AppConnection types for Antonnia events."""

from datetime import datetime
from pydantic import BaseModel


class App(BaseModel):
    """Represents an application that can receive webhook events."""
    
    id: str
    created_at: datetime
    name: str
    webhook: str


class AppConnection(BaseModel):
    """Represents a connection between an app and an organization."""
    
    id: str
    app_id: str
    organization_id: str
    created_at: datetime
    updated_at: datetime 