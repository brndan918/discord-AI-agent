import os

# 加載環境變量 根據情況決定是否使用 須自行擴充
# from dotenv import load_dotenv
# load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

# 基本路徑設置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
COGS_BASE_PATH = os.path.join(
    BASE_DIR,
    "core",
    "cogs",
)

# 確保數據目錄存在
os.makedirs(DATA_DIR, exist_ok=True)

# 日誌設置 根據情況決定是否使用 須自行擴充
# LOGGING_CONFIG = {
#     "level": "INFO",  # 可以設置為 "DEBUG", "INFO", "WARNING", "ERROR"
# }

# 數據文件路徑
DATA_FILES = {
    "discord_agent_data": os.path.join(DATA_DIR, "discord_agent_data.json"),
    # 只留下discord ai agent data
}
