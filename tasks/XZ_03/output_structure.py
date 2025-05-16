from pydantic import BaseModel, Field


class ConfigFile(BaseModel):

    task_path: list = Field(description="Ordered list of coordinates representing the complete path from start to goal")
    task_path_length: float = Field(description="Total path length in meters for Task 1")
    task_algorithm: str = Field(description="Algorithm used for path planning in Task 1 (A*, Dijkstra, etc.)")
    task_nodes_explored: int = Field(description="Number of nodes explored during the search in Task 1")
    task_connectivity: str = Field(description="Whether 4-connected or 8-connected movement was used in Task 1")

# Define your desired output structure
class Response_structure(BaseModel):
    reasoning: str = Field(..., description="Detailed reasoning process to accomplish the task, please solve all the tasks step by step.")
    config: ConfigFile

