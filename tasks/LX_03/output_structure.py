from pydantic import BaseModel, Field


class ConfigFile(BaseModel):
    p1: float = Field(description="the largest peak in (1)")
    p2: float = Field(description="the second largest peak in (1)")
    ts: float = Field(description="settling time in (1)")
    N: float = Field(description="number of peaks in (2)")
    pm: float = Field(description="the largest peak in (2)")
    k1: float = Field(description="an element in K")
    k2: float = Field(description="an element in K")
    k3: float = Field(description="an element in K")
    k4: float = Field(description="an element in K")


# Define your desired output structure
class Response_structure(BaseModel):
    reasoning: str = Field(
        ...,
        description="Detailed reasoning process to accomplish the task, please solve all the tasks step by step.",
    )
    config: ConfigFile
