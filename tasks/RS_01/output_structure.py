from pydantic import BaseModel, Field

class ConfigFile(BaseModel):
    vcarmax: float = Field(description="Max velocity of a car for given setup on a particular track")
    laptime: float = Field(description="Lap time of a car for a given setup on a particular track")


# Define your desired output structure
class Response_structure(BaseModel):
   reasoning: str = Field(..., description="Detailed reasoning process to accomplish the task, please solve all the tasks step by step (include all the calculations).")
   config: ConfigFile
