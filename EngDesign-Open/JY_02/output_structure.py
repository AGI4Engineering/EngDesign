from pydantic import BaseModel, Field 
# from tasks.task_report import EngineeringReport 
 
class ConfigFile(BaseModel): 
    
    gaussian: float =Field( description="the size of the guuassian kernel used to smooth the data")
    edge_x: list[list[float]] =Field( description="the x directional kernel used to filter the edges")
    edge_y: list[list[float]] =Field( description="the y directional kernel used to filter the edges")
    maximum: float = Field( description="the maximum value of the edges to be kept")
    minimum: float = Field( description="the minimum value of the edges to be kept")
    
class Response_structure(BaseModel): 
#    task_report: EngineeringReport 
   reasoning: str = Field(..., description="Detailed reasoning process to accomplish the task, please solve all the tasks step by step.")
   config: ConfigFile
   