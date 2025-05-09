import instructor
from pydantic import BaseModel, Field

class ConfigFile(BaseModel):
    A: list[list[float]] = Field(..., description="State matrix A")
    B: list[list[float]] = Field(..., description="Input matrix B")
    beta: float = Field(..., description="Beta parameter")

# Define your desired output structure
class Response_structure(BaseModel):
    reasoning: str = Field(..., description="Detailed reasoning process to accomplish the task, please solve all the tasks step by step")
    config: ConfigFile