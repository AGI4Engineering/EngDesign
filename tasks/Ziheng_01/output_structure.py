from pydantic import BaseModel, Field


class ConfigFile(BaseModel):
    Ac: float = Field(description="MATLAB code for A_c, e.g. 'Ac = [...];'")
    Bc1: list[float] = Field(description="MATLAB code for B_c1, e.g. 'Bc1 = [...];'")
    Bc2: float = Field(description="MATLAB code for B_c2, e.g. 'Bc2 = [...];'")
    Cc: float = Field(description="MATLAB code for C_c, e.g. 'Cc = [...];'")
    Dc1: list[float] = Field(description="MATLAB code for D_c1, e.g. 'Dc1 = [...];'")
    Dc2: float = Field(description="MATLAB code for D_c2, e.g. 'Dc2 = [...];'")

class Response_structure(BaseModel):
    reasoning: str = Field(..., description="Detailed reasoning process to accomplish the task, please solve all the tasks step by step")
    config: ConfigFile
