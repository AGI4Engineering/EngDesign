import instructor
from pydantic import BaseModel, Field


class config_result(BaseModel):
    over_provisioning: float = Field(description="The over-provisioning value for the configuration")
    num_channels: int = Field(description="The number of channels for the configuration")
    num_chips: int = Field(description="The number of chips for the configuration")
    num_dies: int = Field(description="The number of dies for the configuration")
    num_planes: int = Field(description="The number of planes for the configuration")
    num_blocks: int = Field(description="The number of blocks for the configuration")
    num_pages: int = Field(description="The number of pages for the configuration")

class workload_result(BaseModel):
    res: config_result = Field(description="The configuration result for the workload")

class ConfigFile(BaseModel):
    workloads: list[workload_result] = Field(description="The results of the tuning. The tuned parameter and the final value for each target workload category.")
    workload_names: list[str] = Field(description="The name of the target workload category, correspinding to workloads")
    
# Define your desired output structure
class Response_structure(BaseModel):
    reasoning: str = Field(description="Detailed reasoning process to accomplish the task, please solve all the tasks step by step")
    config: ConfigFile


