import instructor
from pydantic import BaseModel, Field

class ConfigFile(BaseModel):
    lowest_current: float = Field(description="Lowest safe balancing current value in Amperes")
    highest_current: float = Field(description="Highest safe balancing current value in Amperes")
    on_threshold: float = Field(description="SOC value at which the relay switches off charging")
    off_threshold: float = Field(description="SOC value at which the relay switches on charging")

class Response_structure(BaseModel):
    reasoning: str = Field(description="Detailed reasoning process to accomplish the task, please solve all the tasks step by step")
    config: ConfigFile
