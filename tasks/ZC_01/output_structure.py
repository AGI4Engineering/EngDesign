from pydantic import BaseModel, Field
from typing import List

class ConfigFile(BaseModel):
    K: List[float] = Field(description="The state-feedback gain matrix K in shape of 1 times 4")

# Define your desired output structure
class Response_structure(BaseModel):
   reasoning: str = Field(..., description="Detailed reasoning process to accomplish the task, please solve all the tasks step by step.")
   config: ConfigFile
