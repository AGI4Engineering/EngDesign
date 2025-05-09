from pydantic import BaseModel, Field
from tasks.task_report import EngineeringReport
class ConfigFile(BaseModel):
    F_op:list[int] = Field(description="F_op: a list of integers with length 3, which are the operator partition factors on dimensions m, k, and n, respectively.")
    f_t_A_m:int = Field(description="f_t_A_m: integer, which is the temporal partition factor of tensor A on dimension m.")
    f_t_A_k:int = Field(description="f_t_A_k: integer, which is the temporal partition factor of tensor A on dimension k.")
    f_t_B_k:int = Field(description="f_t_B_k: integer, which is the temporal partition factor of tensor B on dimension k.")
    f_t_B_n:int = Field(description="f_t_B_n: integer, which is the temporal partition factor of tensor B on dimension n.")
    f_t_C_m:int = Field(description="f_t_C_m: integer, which is the temporal partition factor of tensor C on dimension m.")
    f_t_C_n:int = Field(description="f_t_C_n: integer, which is the temporal partition factor of tensor C on dimension n.")
# Define your desired output structure
class Response_structure(BaseModel):
    task_report: EngineeringReport
    config: ConfigFile
