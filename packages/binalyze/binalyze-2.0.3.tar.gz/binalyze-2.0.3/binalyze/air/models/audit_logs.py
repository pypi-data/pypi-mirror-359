"""
Audit Logs-related data models for the Binalyze AIR SDK.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import Field

from ..base import AIRBaseModel, Filter


class AuditLog(AIRBaseModel):
    """Audit log entry model matching database schema and API response."""
    
    # Primary identification
    id: int = Field(alias="_id")
    
    # Core audit information
    type: str
    performed_by: str = Field(alias="performedBy")
    description: Optional[str] = None
    
    # Audit data and context
    data: Dict[str, Any]
    organization_ids: List[int] = Field(alias="organizationIds")
    
    # Timestamps
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt") 
    occurred_at: Optional[datetime] = Field(alias="occurredAt", default=None)


class AuditLogsFilter(Filter):
    """Filter for audit logs queries."""
    
    search_term: Optional[str] = None
    organization_ids: Optional[List[int]] = None
    start_date: Optional[str] = Field(default=None, alias="startDate")  # ISO 8601 format
    end_date: Optional[str] = Field(default=None, alias="endDate")      # ISO 8601 format
    user_id: Optional[str] = None
    action: Optional[str] = None
    resource: Optional[str] = None 