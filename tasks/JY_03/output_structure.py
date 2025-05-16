from pydantic import BaseModel, Field 
# from tasks.task_report import EngineeringReport 
 
class ConfigFile(BaseModel): 
    Kernel: list[list[float]] =Field( description="kernel used to fill the black pixels")
    
    
class Response_structure(BaseModel): 
#    task_report: EngineeringReport 
   reasoning: str = Field(..., description="Detailed reasoning process to accomplish the task, please solve all the tasks step by step.")
   config: ConfigFile
   