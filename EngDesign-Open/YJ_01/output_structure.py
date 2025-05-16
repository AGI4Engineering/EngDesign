import instructor
from pydantic import BaseModel, Field

class ConfigFile(BaseModel):
    # y_hat: list[list[float]] = Field(..., description="64x64 optimized material layout. Each value is either 1 (material) or 0 (void).")
    C_y_hat: float = Field(..., description="Compliance of the optimized material layout.")
    VF_y_hat: float = Field(..., description="Volume fraction of the optimized material layout (i.e., the proportion of material used).")
    # load_y_hat: list[list[float]] = Field(..., description="64x64 matrix representing the combined magnitude of x and y directional loads at each node.")
    # floating_material_y_hat: bool = Field(..., description="Boolean indicating whether floating (non-connected) material exists in the layout.")

# Define your desired output structure
class Response_structure(BaseModel):
    reasoning: str = Field(description="Detailed reasoning process to accomplish the task, please solve all the tasks step by step")
    config: ConfigFile