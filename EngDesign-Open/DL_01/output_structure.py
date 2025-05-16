import instructor
from pydantic import BaseModel, Field


class workload_result(BaseModel):
    parameter_names: list[str] = Field(description="The tuned parameter for the workload")
    values: list[str] = Field(description="The corresponding final value of the tuned parameter for the workload. it is eather \"impossible\" or a string that can be converted into float value.")

class ConfigFile(BaseModel):
    workloads: list[workload_result] = Field(description="The results of the tuning. The tuned parameter and the final value for each target workload category.")
    workload_names: list[str] = Field(description="The name of the target workload category, correspinding to workloads")
    
# Define your desired output structure
class Response_structure(BaseModel):
    reasoning: str = Field(description="Detailed reasoning process to accomplish the task, please solve all the tasks step by step")
    config: ConfigFile


