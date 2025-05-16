import instructor
from pydantic import BaseModel, Field

class ConfigFile(BaseModel):
    r: float = Field(..., description="reliable radius")



class Response_structure(BaseModel):
    reasoning: str = Field(..., description="Detailed reasoning process to accomplish the task, please solve all the tasks step by step.")
    config: ConfigFile