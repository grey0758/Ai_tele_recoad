from typing import Annotated
from fastapi import UploadFile
from pydantic import BaseModel, Field



class FileUploadRequest(BaseModel):
    file: Annotated[UploadFile, Field(description="文件")]
    file_uuid: Annotated[str, Field(min_length=36, max_length=36, description="文件唯一标识UUID")]
    description: Annotated[str | None, Field(default=None, description="文件描述")]

    class Config:
        arbitrary_types_allowed = True

class FileUploadResponse(BaseModel):
    file_url: Annotated[str, Field(description="文件URL")]
    