from pydantic import BaseModel, Field


class ConfigFile(BaseModel):
    Th: float = Field(description="The proposed thickness of the L-beam in mm")


class Response_structure(BaseModel):
    reasoning: str = Field(..., description="Detailed reasoning process to accomplish the task, please solve all the tasks step by step.")
    config: ConfigFile
