from pydantic import BaseModel, Field

class ConfigFile(BaseModel):
    write: str = Field(
        ...,
        description="Implementation of the filesystem `write` operation",
        example="def write(fs_img: FileSystemImage, name: str, pos: int, data: str) -> FileSystemImage: \"\"\"Write UTF‑8 bytes of `data` into file `name` at offset `pos` and return the updated image.\"\"\""
    )

class Response_structure(BaseModel):
    reasoning: str = Field(..., description="Detailed reasoning process to accomplish the task, please solve all the tasks step by step.")
    config:      ConfigFile
