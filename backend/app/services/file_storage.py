from pathlib import Path
import hashlib
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import settings


class FileStorageService:
    def __init__(self) -> None:
        self.base_dir = Path(settings.upload_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    async def save_upload(self, file: UploadFile) -> tuple[str, str, str]:
        temp_id = str(uuid4())
        safe_name = f"{temp_id}_{file.filename}"
        path = self.base_dir / safe_name

        content = await file.read()
        path.write_bytes(content)

        content_hash = hashlib.sha256(content).hexdigest()
        return temp_id, str(path), content_hash