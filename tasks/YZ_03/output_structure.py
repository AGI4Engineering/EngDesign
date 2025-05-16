import instructor
from pydantic import BaseModel, Field   
from openai import OpenAI

# Define your desired output structure
class Response_structure(BaseModel):
    reasoning: str = Field(..., description="Detailed reasoning process to accomplish the task, please solve all the tasks step by step.")
    relativeBW: float = Field(description="Relative bandwidth")
    r: float = Field(description="Radius")
    D: float = Field(description="Diameter")
    turns: float = Field(description="Number of turns")
    pitch: float = Field(description="Pitch")
    side: float = Field(description="Side")
    


