from pydantic import BaseModel, Field

class ConfigFile(BaseModel):
    read: str = Field(
        ...,
        description="Implementation of the filesystem `read` operation",
        example="def read(fs_img: FileSystemImage, name: str, pos: int, length: int) -> str: \"\"\"Read up to `length` bytes from file `name` starting at offset `pos`.\"\"\""
    )
    write: str = Field(
        ...,
        description="Implementation of the filesystem `write` operation",
        example="def write(fs_img: FileSystemImage, name: str, pos: int, data: str) -> FileSystemImage: \"\"\"Write UTF‑8 bytes of `data` into file `name` at offset `pos` and return the updated image.\"\"\""
    )
    create: str = Field(
        ...,
        description="Implementation of the filesystem `create` operation",
        example="def create(fs_img: FileSystemImage, path: str, is_dir: bool = False) -> FileSystemImage: \"\"\"Create a new file or directory at `path`, returning the mutated image.\"\"\""
    )
    delete: str = Field(
        ...,
        description="Implementation of the filesystem `delete` operation",
        example="def delete(fs_img: FileSystemImage, path: str) -> FileSystemImage: \"\"\"Delete the entry at `path` and return the updated image.\"\"\""
    )

class Response_structure(BaseModel):
    reasoning: str = Field(..., description="Detailed reasoning process to accomplish the task, please solve all the tasks step by step.")
    config: ConfigFile
