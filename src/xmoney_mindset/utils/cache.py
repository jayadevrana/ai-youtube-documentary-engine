from __future__ import annotations

import hashlib
from pathlib import Path


def stable_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def cached_asset_path(root: Path, namespace: str, key: str, extension: str) -> Path:
    namespace_dir = root / namespace
    namespace_dir.mkdir(parents=True, exist_ok=True)
    filename = f"{stable_hash(key)}.{extension.lstrip('.')}"
    return namespace_dir / filename
