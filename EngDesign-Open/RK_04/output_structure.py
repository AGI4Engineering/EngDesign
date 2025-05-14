from pydantic import BaseModel, Field


class ConfigFile(BaseModel):
    s_hat: float = Field(..., description="max stress of the optimized material layout.")
    VF: float = Field(..., description="Volume fraction of the optimized material layout.")
    Dsg_feature: str = Field(..., description="Design feature of the optimized material layout.")

    


class Response_structure(BaseModel):
    reasoning: str = Field(..., description="Detailed reasoning process to accomplish the task, please solve all the tasks step by step.")
    config: ConfigFile
