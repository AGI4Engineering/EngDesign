import instructor
from pydantic import BaseModel, Field

class ConfigFile(BaseModel):
    angle: float = Field(..., description="Glide angle in degrees (0 < angle < 90)")
    volume: float = Field(..., description="Vehicle volume in cubic meters")
    mass: float = Field(..., description="Mass  in kilograms")


class Response_structure(BaseModel):
    reasoning: str = Field(description="Detailed reasoning process to accomplish the task, please solve all the tasks step by step")
    config: ConfigFile