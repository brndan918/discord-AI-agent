# logging_utils 使用教學

檔案位置: `core/utils/logging_utils/logging_utils.py`

---

## 1. 建立 Logger

```python
from core.utils.logging_utils.logging_utils import log

LOGGER = log.add_logg(
    name="MyLogger",
    level=logging.DEBUG,
    color="magenta"
)
```

---

## 2. 輸出 Log

```python
LOGGER.debug("debug message")
LOGGER.info("info message")
LOGGER.warning("warning message")
LOGGER.error("error message")
LOGGER.critical("critical message")
```

---

## 3. 輸出錯誤 Traceback

```python
LOGGER.error("error occurred", exc_info=True)
```

注意：不要用.exception 請使用.error 再搭配 exc_info=True
