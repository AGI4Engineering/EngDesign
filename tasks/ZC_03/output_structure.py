from pydantic import BaseModel, Field
from typing import List

class ConfigFile(BaseModel):
      bar_alpha: float = Field(description="The upper bound of alpha")
      under_linealpha: float = Field(description="The lower bound of alpha")
      bar_beta: float = Field(description="The upper bound of beta")
      under_linebeta: float = Field(description="The lower bound of beta")

# Define your desired output structure
class Response_structure(BaseModel):
   reasoning: str = Field(..., description="Detailed reasoning process to accomplish the task, please solve all the tasks step by step.")
   config: ConfigFile
