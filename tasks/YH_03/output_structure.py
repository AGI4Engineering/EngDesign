import instructor
from pydantic import BaseModel, Field



class Parameters(BaseModel):
    board_name: float = Field(description="FPGA board name")
    max_DSP: float = Field(description="Maximum DSP resource counts for the given board")
    max_FF: float = Field(description="Maximum FF resource counts for the given board")
    max_LUT: float = Field(description="Maximum LUT resource counts for the given board")
    optimal_DSP: float = Field(description="Maximum DSP resource counts for the given GEMM operation size")
    optimal_FF: float = Field(description="Maximum FF resource counts for the given GEMM operation size")
    optimal_LUT: float = Field(description="Maximum LUT resource counts for the given GEMM operation size")
    m_size: float = Field(description="Required m size by user")
    n_size: float = Field(description="Required n size by user")
    k_size: float = Field(description="Required k size by user")


class ConfigFile(BaseModel):
    ops_num: float = Field(description="The computation operation of the module requested by the user")
    parameters: Parameters = Field(
        description="Information about the FPGA board and operations requested by the user",
        default_factory=Parameters
    )
    hls_design: str = Field(description="C code for HLS design based on the user's request")
    

# Define your desired output structure
class Response_structure(BaseModel):
    reasoning: str = Field(..., description="Detailed reasoning process to accomplish the task, please solve all the tasks step by step.")
    config: ConfigFile
