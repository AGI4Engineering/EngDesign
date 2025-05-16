import instructor
from pydantic import BaseModel, Field

class ConfigFile(BaseModel):
    C_num: list[float] = Field(..., description="numerator coefficients of the controller C(s)")
    C_den: list[float] = Field(..., description="denominator coefficients of the controller C(s)")
    omega_n: float = Field(..., description="parameter of the notch filter")
    alpha_n: float = Field(..., description="parameter of the notch filter")
    f_n: float = Field(..., description="parameter of the notch filter")


# Define your desired output structure
class Response_structure(BaseModel):
    reasoning: str = Field(..., description="Detailed reasoning process to accomplish the task, please solve all the tasks step by step")
    config: ConfigFile