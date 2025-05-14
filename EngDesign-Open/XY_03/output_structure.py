from pydantic import BaseModel, Field

class ConfigFile(BaseModel):
    counter_bits: int = Field(...)
    division_ratio: int = Field(...)
    digit_select_bits: list[int] = Field(...)
    bit_select_reasoning: str = Field(...)
    max_delay_ms: float = Field(...)
    is_flicker_possible: bool = Field(...)
    mitigation_strategy: str = Field(...)

class Response_structure(BaseModel):
    reasoning: str = Field(..., description="Detailedreasoning process to accomplish the task, please solve all the tasks step by step")
    config: ConfigFile