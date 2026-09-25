import json
import aiofiles
import os
import asyncio
from typing import Dict

_locks: Dict[str, asyncio.Lock] = {}

def _get_lock(path: str) -> asyncio.Lock:
    key = os.path.abspath(path)
    if key not in _locks:
        _locks[key] = asyncio.Lock()
    return _locks[key]

async def save_json(file_path: str, data) -> None:
    """
    原子保存 JSON：
    1. 先寫入 file_path.tmp
    2. 完成後再覆蓋原本的 file_path
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    lock = _get_lock(file_path)
    tmp_path = file_path + ".tmp"

    async with lock:
        # 寫入 tmp 檔
        try:
            async with aiofiles.open(tmp_path, "w", encoding="utf-8") as f:
                await f.write(json.dumps(data, ensure_ascii=False, indent=4))
            # 寫完後替換原本 json
            os.replace(tmp_path, file_path)
        finally:
            # 如果程式在建立 tmp 時崩潰，確保 tmp 被清理
            if os.path.exists(tmp_path):
                os.remove(tmp_path)