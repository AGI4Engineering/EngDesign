import instructor
from pydantic import BaseModel, Field

class ConfigFile(BaseModel):
    battery_capacity: float = Field(..., description="Battery capacity in Wh")
    gear_ratio: float = Field(..., description="Gear reduction ratio")
    wheel_diameter: float = Field(..., description="Wheel diameter in meters")
    body_mass: float = Field(..., description="Robot body mass in kilograms")

class Response_structure(BaseModel):
    reasoning: str = Field(..., description="Detailed reasoning process to accomplish the task, please solve all the tasks step by step.")
    config: ConfigFile