import instructor
from pydantic import BaseModel, Field
from openai import OpenAI

class Config(BaseModel):
    coeff_list_1: list[float] = Field(description="List of coefficients for the first polynomial")
    coeff_list_2: list[float] = Field(description="List of coefficients for the second polynomial")

# Define your desired output structure
class Response_structure(BaseModel):
    reasoning: str = Field(..., description="Detailed reasoning process to accomplish the task, please solve all the tasks step by step.")
    config: Config 
    


