from pydantic import BaseModel, Field

class ConfigFile(BaseModel):
    read: str = Field(
        ...,
        description="Implementation of the filesystem `read` operation",
        example="def read(fs_img: FileSystemImage, name: str, pos: int, length: int) -> str: \"\"\"Read up to `length` bytes from file `name` starting at offset `pos`.\"\"\""
    )

class Response_structure(BaseModel):
    reasoning: str = Field(..., description="Detailed reasoning process to accomplish the task, please solve all the tasks step by step.")
    config: ConfigFile
