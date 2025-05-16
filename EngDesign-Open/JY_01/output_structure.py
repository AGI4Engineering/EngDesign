from pydantic import BaseModel, Field
 
class ConfigFile(BaseModel): 
    angle12: float =Field( description="value of the angle of the first linear polarizing filter")
    angle22: float =Field( description="value of the angle of the second quater wave plate")
    angle32: float =Field( description="value of the angle of the third linear polarizing filter")
# Define your desired output structure
class Response_structure(BaseModel):
   reasoning: str = Field(..., description="Detailed reasoning process to accomplish the task, please solve all the tasks step by step.")
   config: ConfigFile
