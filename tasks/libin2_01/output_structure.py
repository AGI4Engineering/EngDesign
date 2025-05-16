from pydantic import BaseModel, Field


class DeviceConfig(BaseModel):
    page_size: int = Field(description="Page size in bytes")
    levels: int = Field(description="Number of page table levels")
    entries_per_level: list[int] = Field(description="Number of entries in each level")
    page_table_memory: int = Field(description="Total page table memory overhead in bytes")
    avg_translation_time: float = Field(description="Average address translation time in ns")

class ConfigFile(BaseModel):
    DeviceA: DeviceConfig = Field(description="Configuration for Device A")
    DeviceB: DeviceConfig = Field(description="Configuration for Device B")


# Define your desired output structure
class Response_structure(BaseModel):
   reasoning: str = Field(..., description="Detailed reasoning process to accomplish the task, please solve all the tasks step by step.")
   config: ConfigFile
