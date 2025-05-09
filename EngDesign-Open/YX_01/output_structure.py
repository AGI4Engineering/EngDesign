import instructor
from pydantic import BaseModel, Field
from openai import OpenAI


class ConfigFile(BaseModel):
    Bottom_left: tuple = Field(description="Tuple representing the coordinates of the vertex in the bottom-left corner of the costmap")   # For Task 1
    Bottom_right: tuple = Field(description="Tuple representing the coordinates of the vertex in the bottom-right corner of the costmap") # For Task 1
    Top_right: tuple = Field(description="Tuple representing the coordinates of the vertex in the top-right corner of the costmap")       # For Task 1
    Top_left: tuple = Field(description="Tuple representing the coordinates of the vertex in the top-left corner of the costmap")         # For Task 1
    task2_length: float = Field(description="Float representing the total path length for Task 2")    # For Task 2
    tol2: float = Field("The absolute error in Task 2")
    task3_length: float = Field(description="Float representing the total path length for Task 3")    # For Task 3
    tol3: float = Field("The absolute error in Task 3")


# Define your desired output structure
class Response_structure(BaseModel):
   reasoning: str = Field(..., description="Detailed reasoning process to accomplish the task, please solve all the tasks step by step.")
   config: ConfigFile

