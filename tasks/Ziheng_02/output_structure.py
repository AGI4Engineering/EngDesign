from pydantic import BaseModel, Field


class ConfigFile(BaseModel):
    theta: list[float] = Field(
        ...,
        description="Joint angles [θ1,...,θ6] as a list of floats"
    )

class Response_structure(BaseModel):
    reasoning: str = Field(..., description="Detailed reasoning process to accomplish the task, please solve all the tasks step by step")
    config: ConfigFile
