"""PaymentDetails DTO model."""
from pydantic import Field

from .base_dto import DTOBase

class PaymentDetails(DTOBase):
    """Model for payment details."""
    card_network: str = Field(alias='cardNetwork')
    card_type: str
    method_id: str = Field(alias='methodId')
    method_type: str = Field(alias='methodType')
    name: str
    type: str
