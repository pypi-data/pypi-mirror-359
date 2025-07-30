"""License models for Binalyze AIR SDK."""

from typing import Optional
from datetime import datetime
from pydantic import Field

from ..base import AIRBaseModel


class License(AIRBaseModel):
    """Represents a license in the Binalyze AIR system.
    
    Attributes:
        id: The license key identifier (maps to _id in database)
        is_locked_down: Whether the license is in locked down mode
        activated_on: When the license was activated
        period_days: Total license period in days
        remaining_days: Remaining days until expiration
        expires_on: License expiration date
        device_count: Current number of devices
        max_device_count: Maximum allowed devices
        client_count: Current number of clients
        max_client_count: Maximum allowed clients
        model: License model type
        is_lifetime: Whether this is a lifetime license
        customer_name: Name of the customer
        created_at: When the license record was created
        updated_at: When the license record was last updated
    """
    # Primary identification (from API response key field)
    id: str = Field(alias="key")
    
    # License status and configuration
    is_locked_down: bool = Field(alias="isLockedDown")
    activated_on: datetime = Field(alias="activatedOn")
    period_days: int = Field(alias="periodDays")
    remaining_days: int = Field(alias="remainingDays")
    expires_on: datetime = Field(alias="expiresOn")
    
    # Usage counts
    device_count: int = Field(alias="deviceCount")
    max_device_count: int = Field(alias="maxDeviceCount")
    client_count: int = Field(alias="clientCount")
    max_client_count: int = Field(alias="maxClientCount")
    
    # License type and customer info
    model: int
    is_lifetime: bool = Field(alias="isLifetime")
    customer_name: Optional[str] = Field(alias="customerName", default=None)
    
    # Timestamps (these may not be in API response)
    created_at: Optional[datetime] = Field(alias="createdAt", default=None)
    updated_at: Optional[datetime] = Field(alias="updatedAt", default=None)

    def is_expired(self) -> bool:
        """Check if the license is expired.
        
        Returns:
            True if license is expired, False otherwise
        """
        return self.remaining_days <= 0

    def is_near_expiry(self, days_threshold: int = 30) -> bool:
        """Check if license is near expiry.
        
        Args:
            days_threshold: Number of days to consider as near expiry
            
        Returns:
            True if license expires within threshold days
        """
        return self.remaining_days <= days_threshold

    def get_usage_percentage(self) -> dict:
        """Get usage percentages for devices and clients.
        
        Returns:
            Dictionary with device and client usage percentages
        """
        device_usage = (
            (self.device_count / self.max_device_count * 100) 
            if self.max_device_count > 0 else 0
        )
        client_usage = (
            (self.client_count / self.max_client_count * 100) 
            if self.max_client_count > 0 else 0
        )
        
        return {
            'device_usage_percent': round(device_usage, 2),
            'client_usage_percent': round(client_usage, 2)
        }


class LicenseUpdateRequest(AIRBaseModel):
    """Request model for updating license.
    
    Attributes:
        license_key: The new license key to set
    """
    license_key: str = Field(alias="licenseKey") 