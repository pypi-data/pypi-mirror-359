import uuid
import os
from fastapi import UploadFile

async def save_upload_file(upload_file: UploadFile) -> str:
    ext = os.path.splitext(upload_file.filename)[1]
    temp_path = f"/tmp/{uuid.uuid4()}{ext}"
    with open(temp_path, "wb") as buffer:
        content = await upload_file.read()
        buffer.write(content)
    return temp_path

import aiohttp

async def download_file_from_url(url: str) -> str:
    import aiohttp
    import uuid
    import os

    ext = os.path.splitext(url)[1] or ".tmp"
    temp_path = f"/tmp/{uuid.uuid4()}{ext}"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                raise Exception(f"Failed to download file, status {resp.status}")
            with open(temp_path, "wb") as f:
                while True:
                    chunk = await resp.content.read(1024)
                    if not chunk:
                        break
                    f.write(chunk)
    return temp_path
