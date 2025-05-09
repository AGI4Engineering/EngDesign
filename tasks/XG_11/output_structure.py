import instructor
from pydantic import BaseModel, Field

class ConfigFile(BaseModel):
    C_num: list[float] = Field(..., description="numerator coefficients of the controller C(s) with shape [1,2]")
    C_den: list[float] = Field(..., description="denominator coefficients of the controller C(s) with shape [1,2]")
    omega_r: float = Field(..., description="parameter of the roll-off filter")
    beta_r: float = Field(..., description="parameter of the roll-off filter")


# Define your desired output structure
class Response_structure(BaseModel):
    reasoning: str = Field(..., description="Detailed reasoning process to accomplish the task, please solve all the tasks step by step")
    config: ConfigFile