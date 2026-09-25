# JSON Utils 使用說明: **異步安全讀寫 JSON，避免同時存取造成檔案損壞。**

## 導入
```python
from core.utils.json_utils import load_json, save_json
```

## 讀取 JSON
```python
data = await load_json("data/example.json")
```

## 特性

* 檔案不存在 → 回傳 `{}`
* 自動清理 `.tmp`
* 多協程安全

---

## 儲存 JSON

```python
await save_json("data/example.json", data)
```

特性：

* 原子寫入 (`.tmp` → 覆蓋)
* 自動建立資料夾
* 多協程安全

---

## 簡單範例

```python
config = await load_json("config/settings.json")

config["prefix"] = "!"

await save_json("config/settings.json", config)
```
