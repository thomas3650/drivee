"""DTO for payment details data transfer."""
from __future__ import annotations

from typing import Literal

from .base_dto import BaseDTO
from pydantic import Field

class PaymentDetailsDTO(BaseDTO):
    """DTO representing payment method details.
    
    Contains information about the payment method used for a transaction,
    including card details and payment method type.
    """
    
    # Payment method fields
    card_network: Literal["visa", "mastercard", "amex", "discover", "other"] = Field(..., alias="cardNetwork")
    card_type: Literal["credit", "debit", "prepaid", "other"] = Field(..., alias="card_type")
    method_id: str = Field(..., alias="methodId")
    method_type: Literal["card", "bank", "wallet", "other"] = Field(..., alias="method_type")
    name: str = Field(..., alias="name")
    type: str = Field(..., alias="type")
