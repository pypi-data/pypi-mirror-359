from pydantic import BaseModel, HttpUrl
from typing import Optional

class TranscriptRequest(BaseModel):
    file: Optional[bytes] = None  # For file upload (optional, handled by FastAPI File)
    url: Optional[HttpUrl] = None
