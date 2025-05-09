import instructor
from pydantic import BaseModel, Field
from openai import OpenAI

# Define your desired output structure
class Response_structure(BaseModel):
    reasoning: str = Field(..., description="Detailed reasoning process to accomplish the task, please solve all the tasks step by step.")
    numCells_p: float = Field(description="Number of cells in the positive electrode")
    numCells_s: float = Field(description="Number of cells in the separator")
    NumChannel: float = Field(description="Number of channels")
    Flowrate: float = Field(description="Flow rate")
    ChannelDia: float = Field(description="Channel diameter")
    


