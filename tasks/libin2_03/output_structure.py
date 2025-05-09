from pydantic import BaseModel, Field

class ConfigFile(BaseModel):
    cluster_kb: int = Field(description="Chosen cluster size in KB")
    small_threshold_kb: int = Field(description="Small-file threshold T in KB")
    frag_overhead: float = Field(description="Calculated fragmentation overhead percentage, four decimal places")
    meta_overhead: float = Field(description="Calculated metadata overhead percentage, four decimal places")


# Define your desired output structure
class Response_structure(BaseModel):
   reasoning: str = Field(..., description="Detailed reasoning process to accomplish the task, please solve all the tasks step by step.")
   config: ConfigFile
