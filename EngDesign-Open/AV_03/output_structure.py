import instructor
from pydantic import BaseModel, Field

class ConfigFile(BaseModel):
    order: float = Field(description="The order of the filter")
    coeffs: list[float] = Field(description="The list of filter coefficients")
    stpbnd: float = Field(description="The beginning frequency of the stopband")
    decim: float = Field(description="The decimation factor")

# Define your desired output structure
class Response_structure(BaseModel):
    reasoning: str = Field(..., description="Detailed reasoning process to accomplish the task, please solve all the tasks step by step.")
    config: ConfigFile
