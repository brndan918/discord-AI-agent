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

async def load_json(file_path: str) -> dict:
    """
    安全讀取 JSON：
    1. 發現 tmp 則刪除 tmp
    2. 再讀取原本的 json
    """
    tmp_path = file_path + ".tmp"
    if os.path.exists(tmp_path):
        os.remove(tmp_path)  # 清理殘留 tmp

    if not os.path.exists(file_path):
        return {}

    lock = _get_lock(file_path)
    async with lock:
        async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
            content = await f.read()
    return json.loads(content)