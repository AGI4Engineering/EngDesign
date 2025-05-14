from pydantic import BaseModel, Field

class ConfigFile(BaseModel):
    color_mapping: dict = Field(description="Mapping of visual elements to their assigned RGB444 colors.")
    display_regions: dict = Field(description="Definition of screen regions with pixel coordinate boundaries.")
    tetromino_colors: list = Field(description="Color schemes including default, highlight, and shadow for each tetromino type.")
    ui_elements: dict = Field(description="UI color configurations for start menu and game over screens.")
    bit_slicing: dict = Field(description="Bit slicing expressions for pixel-to-grid position mapping.")
    dynamic_modes: dict = Field(description="Color adjustments applied during dynamic gameplay modes like Night Mode.")
    resource_constraints: dict = Field(description="Statement about adherence to 10-color active limit constraint.")

class Response_structure(BaseModel):
    reasoning: str = Field(..., description="Detailedreasoning process to accomplish the task, please solve all the tasks step by step")
    config: ConfigFile
