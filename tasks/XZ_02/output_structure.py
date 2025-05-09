import instructor
from pydantic import BaseModel, Field
from openai import OpenAI


class ConfigFile(BaseModel):
    
    path: list = Field(description="Sequence of poses (x, y, θ) representing the path at regular intervals")
    path_length: float = Field(description="Total path length in meters")
    algorithm: str = Field(description="Algorithm used for path planning (RRT, RRT*, Hybrid A*, etc.)")
    min_obstacle_distance: float = Field(description="Minimum distance to obstacles along the path in meters")
    max_curvature: float = Field(description="Maximum curvature along the path (should be ≤ 0.25 to satisfy turning radius constraint)")
    constraints_satisfied: bool = Field(description="Whether the path satisfies all constraints (obstacle clearance and turning radius)")
    computation_time: float = Field(description="Computation time in seconds")
    nodes_explored: int = Field(description="Number of nodes/states explored during planning")


# Define your desired output structure
class Response_structure(BaseModel):
    reasoning: str = Field(..., description="Detailed reasoning process to accomplish the task, please solve all the tasks step by step.")
    config: ConfigFile

