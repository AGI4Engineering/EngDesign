import instructor
from pydantic import BaseModel, Field
from openai import OpenAI

class Config(BaseModel):
    Fpass: float = Field(..., description="The passband frequency in Hz")
    Fstop: float = Field(..., description="The stopband frequency in Hz")
    Ast: float = Field(..., description="The stopband attenuation in dB")
    Ap: float = Field(..., description="The passband ripple in dB")
    Factor_1: float = Field(..., description="The first factor")
    Factor_2: float = Field(..., description="The second factor")

# Define your desired output structure
class Response_structure(BaseModel):
    reasoning: str = Field(..., description="Detailed reasoning process to accomplish the task, please solve all the tasks step by step.")
    config: Config
    


