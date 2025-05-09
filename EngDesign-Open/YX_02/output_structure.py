import instructor
from pydantic import BaseModel, Field
from typing import List
from openai import OpenAI

class ConfigFile(BaseModel):
    # For Task 1
    constraint_parameters: List[float] = Field(description="The linear constraint parameters [a, b] defining F_max = a * N + b")
    # For Task 2
    global_design_points: List[List[float]] = Field(description="List of [N, F] global design points generated using LHS that satisfy the physical constraint")
    # For Task 3
    normalized_speed_factor: float = Field(description="The normalized speed factor f")
    P_range: List[float] = Field(description="Interpolated lower and upper bounds for fuel pressure (P) in MPa")
    G_range: List[float] = Field(description="Interpolated lower and upper bounds for turbo rack position (G) in ratio")
    # For Task 4
    local_design_points: List[List[float]] = Field(description="List of local design points sampled using Latin Hypercube Sampling. Each tuple represents one point in the form [S, P, G, E], where S is injection, P is fuel pressure, G is turbo rack position, and E is EGR valve lift")


# Define your desired output structure
class Response_structure(BaseModel):
   reasoning: str = Field(..., description="Detailed reasoning process to accomplish the task, please solve all the tasks step by step.")
   config: ConfigFile

