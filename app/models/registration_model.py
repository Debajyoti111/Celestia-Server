from pydantic import BaseModel, Field

# Registration Model
class RegistrationModel(BaseModel):
    phone_number: str = Field(..., example="08123456789")