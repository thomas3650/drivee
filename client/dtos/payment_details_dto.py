"""DTO for payment details data transfer."""
from typing import Literal
from pydantic import Field

from .base_dto import BaseDTO

CardNetworkType = Literal["visa", "mastercard", "amex", "discover", "other"]
CardType = Literal["credit", "debit", "prepaid", "other"]
PaymentMethodType = Literal["card", "bank", "wallet", "other"]

class PaymentDetailsDTO(BaseDTO):
    """DTO representing payment method details.
    
    Contains information about the payment method used for a transaction,
    including card details and payment method type.
    """
    card_network: CardNetworkType = Field(
        alias='cardNetwork',
        description="Card network (e.g., Visa)"
    )
    card_type: CardType = Field(
        description="Type of card (e.g., credit)"
    )
    method_id: str = Field(
        alias='methodId',
        description="Unique payment method identifier"
    )
    method_type: PaymentMethodType = Field(
        alias='methodType',
        description="Type of payment method"
    )
    name: str = Field(description="Display name of payment method")
    type: str = Field(description="Specific type identifier")
