from pydantic import BaseModel, Field

class ConfigFile(BaseModel):
    # Design inputs
    length_mm: float = Field(description="Length of the patch in millimeters")
    width_mm: float = Field(description="Width of the patch in millimeters")
    height_mm: float = Field(description="Substrate height in millimeters")
    epsilon_r: float = Field(description="Relative permittivity of the substrate")
    feed_offset_x_mm: float = Field(description="Feed offset along the x-axis in millimeters")

class Response_structure(BaseModel):
    reasoning: str = Field(..., description="Detailed reasoning process to accomplish the task, please solve all the tasks step by step")
    config: ConfigFile    
