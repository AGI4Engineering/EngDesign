import instructor
from pydantic import BaseModel, Field

class ConfigFile(BaseModel):
    order: float = Field(description="The order of the filter")
    coeffs_numerator: list[float] = Field(description="The list of filter numerator coefficients")
    coeffs_denominator: list[float] = Field(description="The list of filter denominator coefficients")

# Define your desired output structure
class Response_structure(BaseModel):
    reasoning: str = Field(..., description="Detailed reasoning process to accomplish the task, please solve all the tasks step by step.")
    config: ConfigFile
