from .base_model import BaseModel
from ..dtos.charging_responses_dto import ChargingResponseDTO
from .charging_session import ChargingSession

class ChargingResponseModel(BaseModel[ChargingResponseDTO]):
   
    def __init__(self, dto: ChargingResponseDTO) -> None:
        super().__init__(dto)
        self.validate_business_rules()
 
    @property
    def session(self) -> ChargingSession:
        """Get the session as a business model."""
        return ChargingSession(self._dto.session)

    def validate_business_rules(self) -> None:
        """Validate that this charging response satisfies all business rules.
        - Must have a valid session
        Raises:
            BusinessRuleError: If any business rule is violated
        """
