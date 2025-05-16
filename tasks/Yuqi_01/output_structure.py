from pydantic import BaseModel, Field
# from tasks.task_report import EngineeringReport

class ConfigFile(BaseModel):
    # Task 1
    max_width_SA: int = Field(description="The maximum width of the SA. Used in Task 1.")

    # Task 2
    HBM_bandwidth_GBps: float = Field(description="The HBM bandwidth in GBps. Used in Task 2.")

    # Task 3
    prefill_DP: int = Field(description="Data parallelism degree. Must be a multiple of 2. Used in Task 3 for prefill.")
    prefill_TP: int = Field(description="Tensor parallelism degree. Must be a multiple of 2. Used in Task 3 for prefill.")
    prefill_PP: int = Field(description="Pipeline parallelism degree. Must be a multiple of 2. Used in Task 3 for prefill.")
    prefill_batch_size: int = Field(description="Number of requests in a batch. Must be a power of 2. Used in Task 3 for prefill.")
    # This is currently only used for debugging, and will not be used to evaluate the answer.
    prefill_mem_per_chip_GB: float = Field(description="Memory per chip in GB. Used in Task 3 for prefill.")

    decode_DP: int = Field(description="Data parallelism degree. Must be a multiple of 2. Used in Task 3 for decode.")
    decode_TP: int = Field(description="Tensor parallelism degree. Must be a multiple of 2. Used in Task 3 for decode.")
    decode_PP: int = Field(description="Pipeline parallelism degree. Must be a multiple of 2. Used in Task 3 for decode.")
    decode_batch_size: int = Field(description="Number of requests in a batch. Must be a power of 2. Used in Task 3 for decode.")
    # This is currently only used for debugging, and will not be used to evaluate the answer.
    decode_mem_per_chip_GB: float = Field(description="Memory per chip in GB. Used in Task 3 for decode.")


# Define your desired output structure
class Response_structure(BaseModel):
    reasoning: str = Field(..., description="Detailed reasoning process to accomplish the task, please solve all the tasks step by step.")
    config: ConfigFile
