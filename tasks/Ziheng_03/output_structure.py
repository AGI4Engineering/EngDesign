from pydantic import BaseModel, Field


class ConfigFile(BaseModel):
    Kp: float = Field(..., description="Proportional gain (Kp) as a plain number")
    Ki: float = Field(..., description="Integral gain (Ki) as a plain number")
    Kd: float = Field(..., description="Derivative gain (Kd) as a plain number")

class Response_structure(BaseModel):
    reasoning: str = Field(..., description="Detailed reasoning process to accomplish the task, please solve all the tasks step by step")
    config: ConfigFile
