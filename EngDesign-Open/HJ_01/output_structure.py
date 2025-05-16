from pydantic import BaseModel, Field

class ConfigFile(BaseModel):
    refresh_rate: int = Field(description="Refresh rate in Hz")
    acceleration: float = Field(description="Acceleration in m/s²")
    max_velocity: float = Field( description="Maximum velocity in m/s")
    lookahead_distance: float = Field( description="Lookahead distance in meters")
    
# Define your desired output structure
class Response_structure(BaseModel):
   reasoning: str = Field(..., description="Detailed reasoning process to accomplish the task, please solve all the tasks step by step.")
   config: ConfigFile

   
