import instructor
from pydantic import BaseModel, Field


class ConfigFile(BaseModel):
    MISSING_type1: str = Field(..., description="Type of membership function 1")
    MISSING_parameters1: list[float] = Field(..., description="Parameters of membership function 1")    
    MISSING_type2: str = Field(..., description="Type of membership function 2")
    MISSING_parameters2: list[float] = Field(..., description="Parameters of membership function 2")
    MISSING_type3: str = Field(..., description="Type of membership function 3")
    MISSING_parameters3: list[float] = Field(..., description="Parameters of membership function 3")
    MISSING_type4: str = Field(..., description="Type of membership function 4")
    MISSING_parameters4: list[float] = Field(..., description="Parameters of membership function 4")
    MISSING_type5: str = Field(..., description="Type of membership function 5")
    MISSING_parameters5: list[float] = Field(..., description="Parameters of membership function 5")
    MISSING_type6: str = Field(..., description="Type of membership function 6")
    MISSING_parameters6: list[float] = Field(..., description="Parameters of membership function 6")
    MISSING_type7: str = Field(..., description="Type of membership function 7")
    MISSING_parameters7: list[float] = Field(..., description="Parameters of membership function 7")
    MISSING_type8: str = Field(..., description="Type of membership function 8")
    MISSING_parameters8: list[float] = Field(..., description="Parameters of membership function 8")
    MISSING_rule_list: list[list[int]] = Field(..., description="Rule list")
    MISSING_tip1: float = Field(..., description="Tip for input 1")
    MISSING_tip2: float = Field(..., description="Tip for input 2")


# Define your desired output structure
class Response_structure(BaseModel):
    reasoning: str = Field(..., description="Detailed reasoning process to accomplish the task, please solve all the tasks step by step")
    config: ConfigFile