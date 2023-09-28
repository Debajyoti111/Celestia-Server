from pydantic import BaseModel, Field

# Registration Model
class MonitorModel(BaseModel):
    phone_number: str = Field(..., example="08123456789")
    game_type: str = Field(..., example="game1")