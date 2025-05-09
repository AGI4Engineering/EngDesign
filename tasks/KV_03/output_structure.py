import instructor
from pydantic import BaseModel, Field

class ConfigFile(BaseModel):
    A: str = Field(description="Simulink block or logic for label A")
    B: str = Field(description="Simulink block or logic for label B")
    C: str = Field(description="Simulink block or logic for label C")
    D: str = Field(description="Simulink block or logic for label D")
    E: str = Field(description="Simulink block or logic for label E")
    F: str = Field(description="Simulink block or logic for label F")
    G: str = Field(description="Simulink block or logic for label G")
    I: str = Field(description="Simulink block or logic for label I")
    J: str = Field(description="Simulink block or logic for label J")

class Response_structure(BaseModel):
    reasoning: str = Field(description="Detailed reasoning process to accomplish the task, please solve all the tasks step by step")
    config: ConfigFile
