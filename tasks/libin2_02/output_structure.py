from pydantic import BaseModel, Field

class CaseMetrics(BaseModel):
    avg_waiting_time: float = Field(description="Average waiting time in ms")
    context_switches: int = Field(description="Number of context switches")
    quantum_cost: float = Field(description="Time quantum cost in ms")

class ConfigFile(BaseModel):
    time_quantum: int = Field(description="Chosen time quantum in ms")
    case1: CaseMetrics = Field(description="Metrics for case1")
    case2: CaseMetrics = Field(description="Metrics for case2")
    case3: CaseMetrics = Field(description="Metrics for case3")


# Define your desired output structure
class Response_structure(BaseModel):
   reasoning: str = Field(..., description="Detailed reasoning process to accomplish the task, please solve all the tasks step by step.")
   config: ConfigFile
