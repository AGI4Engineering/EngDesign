from pydantic import BaseModel, Field
from tasks.task_report import EngineeringReport

class ConfigFile(BaseModel):
 code: str = Field(description="SystemVerilog code defining the multi-entry, zero-latency FIFO. Produce in json with \n at each line break")

# Define your desired output structure
class Response_structure(BaseModel):
 task_report: EngineeringReport
 config: ConfigFile


# from pydantic import BaseModel, Field

# class ResponseStructure(BaseModel):
#     """
#     We expect the LLM to return exactly one field:
#       • code: the SystemVerilog source for module fifo2.
#     """
#     code: str = Field(
#         description="SystemVerilog source text defining the fifo2 module."
#     )
