import instructor
from pydantic import BaseModel, Field

class ConfigFile(BaseModel):
    a: float = Field(description="Estimated coefficient of the second order term")
    b: float = Field(description="Estimated coefficient of the first order term")
    c: float = Field(description="Estimated bias")

# Define your desired output structure
class Response_structure(BaseModel):
    reasoning: str = Field(..., description="Detailed reasoning process to accomplish the task, please solve all the tasks step by step.")
    config: ConfigFile