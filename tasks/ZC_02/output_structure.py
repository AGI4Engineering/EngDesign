from pydantic import BaseModel, Field
from typing import List

class ConfigFile(BaseModel):
      alpha: float = Field(description="The stability margin")

# Define your desired output structure
class Response_structure(BaseModel):
   reasoning: str = Field(..., description="Detailed reasoning process to accomplish the task, please solve all the tasks step by step.")
   config: ConfigFile
