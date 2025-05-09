from pydantic import BaseModel, Field


class ConfigFile(BaseModel):
    force_on_neck: float = Field(description="Maximum force (in Newton) on neck when going thorugh a corner")


# Define your desired output structure
class Response_structure(BaseModel):
    reasoning: str = Field(description="Detailed reasoning process to accomplish the task, please solve all the tasks step by step.")
    config: ConfigFile