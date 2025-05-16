import instructor
from pydantic import BaseModel, Field
from openai import OpenAI

class ConfigFile(BaseModel):
    Kp: float = Field(..., description="The proportional gain.")
    Ki: float = Field(..., description="The integral gain.")
    Kd: float = Field(..., description="The derivative gain.")

# Define your desired output structure
class Response_structure(BaseModel):
    reasoning: str = Field(..., description="Detailed reasoning process to accomplish the task, please solve all the tasks step by step.")
    config: ConfigFile