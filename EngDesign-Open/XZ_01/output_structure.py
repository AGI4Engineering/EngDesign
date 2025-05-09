from pydantic import BaseModel, Field


class ConfigFile(BaseModel):

    task1_path: list = Field(description="Ordered list of coordinates representing the complete path from start to goal")
    task1_path_length: float = Field(description="Total path length in meters for Task 1")
    task1_algorithm: str = Field(description="Algorithm used for path planning in Task 1 (A*, Dijkstra, etc.)")
    task1_nodes_explored: int = Field(description="Number of nodes explored during the search in Task 1")
    task1_connectivity: str = Field(description="Whether 4-connected or 8-connected movement was used in Task 1")
    task1_execution_time: float = Field(description="Execution time of the algorithm for Task 1 (optional)", default=None)

# Define your desired output structure
class Response_structure(BaseModel):
    reasoning: str = Field(..., description="Detailed reasoning process to accomplish the task, please solve all the tasks step by step.")
    config: ConfigFile

