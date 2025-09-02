"""DTO for payment details data transfer."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Optional

from .base_dto import BaseDTO

@dataclass
class PaymentDetailsDTO(BaseDTO):  # type: ignore[type-arg]
    """DTO representing payment method details.
    
    Contains information about the payment method used for a transaction,
    including card details and payment method type.
    """
    # Required fields from BaseDTO
    id: str
    
    # Optional fields from BaseDTO
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    # Payment method fields
    card_network: Literal["visa", "mastercard", "amex", "discover", "other"] = "other"
    card_type: Literal["credit", "debit", "prepaid", "other"] = "other"
    method_id: str = ""
    method_type: Literal["card", "bank", "wallet", "other"] = "other"
    name: str = ""  # Display name of payment method
    type: str = ""  # Specific type identifier
