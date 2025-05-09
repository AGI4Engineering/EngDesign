from pydantic import BaseModel, Field


class ConfigFile(BaseModel):
    max_acc: float = Field(description="Maximum acceleration of the car")
    max_dec: float = Field(description="Maximum deceleration of the car")


# Define your desired output structure
class Response_structure(BaseModel):
    reasoning: str = Field(description="Detailed reasoning process to accomplish the task, please solve all the tasks step by step.")
    config: ConfigFile