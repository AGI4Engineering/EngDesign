from pydantic import BaseModel, Field

class ConfigFile(BaseModel):
    # Design inputs
    height_mm: float = Field(description="Height of the cylindrical monopole in millimeters")
    radius_mm: float = Field(description="Radius of the cylindrical monopole in millimeters")

class Response_structure(BaseModel):
    reasoning: str = Field(..., description="Detailed reasoning process to accomplish the task, please solve all the tasks step by step")
    config: ConfigFile    
