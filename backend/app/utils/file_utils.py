import re
from pathlib import Path
from uuid import uuid4


def sanitize_filename(filename: str) -> str:
    base_name = Path(filename).name
    safe_name = re.sub(r"[^A-Za-z0-9._-]", "_", base_name)
    return safe_name or f"upload_{uuid4().hex}.bin"


def build_storage_filename(filename: str) -> str:
    sanitized = sanitize_filename(filename)
    return f"{uuid4().hex}_{sanitized}"
