from pydantic import BaseModel, Field


class ConfigFile(BaseModel):
    a11: float = Field(description="an element in A")
    a12: float = Field(description="an element in A")
    a21: float = Field(description="an element in A")
    a22: float = Field(description="an element in A")
    b11: float = Field(description="an element in B")
    b21: float = Field(description="an element in B")
    k1: float = Field(description="an element in K")
    k2: float = Field(description="an element in K")
    l1: float = Field(description="an element in L")
    l2: float = Field(description="an element in L")
    s1: int = Field(description="is i.c.(a) within the region of asymptotic stability")
    s2: int = Field(description="is i.c.(b) within the region of asymptotic stability")
    s3: int = Field(description="is i.c.(c) within the region of asymptotic stability")
    s4: int = Field(description="is i.c.(d) within the region of asymptotic stability")


# Define your desired output structure
class Response_structure(BaseModel):
    reasoning: str = Field(..., description="Detailed reasoning process to accomplish the task, please solve all the tasks step by step.")
    config: ConfigFile
