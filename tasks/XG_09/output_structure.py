import instructor
from pydantic import BaseModel, Field

class ConfigFile(BaseModel):
    sx: float = Field(..., description="parameter for the membership function Ix")
    sy: float = Field(..., description="parameter for the membership function Iy")
    wa: float = Field(..., description="parameter for the membership function Iout")
    wb: float = Field(..., description="parameter for the membership function Iout")
    wc: float = Field(..., description="parameter for the membership function Iout")
    ba: float = Field(..., description="parameter for the membership function Iout")
    bb: float = Field(..., description="parameter for the membership function Iout")
    bc: float = Field(..., description="parameter for the membership function Iout")


# Define your desired output structure
class Response_structure(BaseModel):
    reasoning: str = Field(..., description="Detailed reasoning process to accomplish the task, please solve all the tasks step by step")
    config: ConfigFile