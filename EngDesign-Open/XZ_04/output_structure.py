from pydantic import BaseModel, Field
from typing import List, Tuple


class TrajectoryPoint(BaseModel):
    time: float = Field(..., description="Time point (in seconds)")
    x: float = Field(..., description="X coordinate (in meters)")
    y: float = Field(..., description="Y coordinate (in meters)")
    z: float = Field(..., description="Z coordinate (in meters)")
    velocity: float = Field(..., description="Velocity at this point (in m/s)")
    acceleration: float = Field(..., description="Acceleration at this point (in m/s²)")


class ConfigFile(BaseModel):
    trajectory: List[TrajectoryPoint] = Field(..., description="Complete ordered list of trajectory points in format (t, X, Y, Z, v, a)")
    path_length: float = Field(..., description="Total path length in meters")
    travel_time: float = Field(..., description="Total travel time in seconds")
    nodes_explored: int = Field(..., description="Number of nodes explored during the search")
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "trajectory": [
                        {"time": 0.0, "x": 0.0, "y": 0.0, "z": 0.0, "velocity": 0.0, "acceleration": 0.0},
                        {"time": 10.0, "x": 19.0, "y": 24.0, "z": 0.0, "velocity": 0.0, "acceleration": 0.0}
                    ],
                    "path_length": 30.61,
                    "travel_time": 25.5,
                    "nodes_explored": 1245
                }
            ]
        }


class Response_structure(BaseModel):
    reasoning: str = Field(..., description="Detailed reasoning process to accomplish the task, including path planning approach, handling of speed constraints in different zones, obstacle avoidance strategy, and ensuring the trajectory stays within allowed zones (WHITE_ZONE, RED_ZONE, GREEN_ZONE).")
    config: ConfigFile = Field(..., description="Configuration containing trajectory and metrics")