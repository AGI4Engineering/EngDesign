import instructor
from pydantic import BaseModel, Field

class ConfigFile(BaseModel):
    num: list[float] = Field(description="List of numerator coefficients of the desired loop shape")
    den: list[float] = Field(description="List of denominator coefficients of the desired loop shape")
    alpha: float = Field(description="Alpha value for loopsyn")

# Define your desired output structure
class Response_structure(BaseModel):
    reasoning: str = Field(..., description="Detailed reasoning process to accomplish the task, please solve all the tasks step by step")
    config: ConfigFile
