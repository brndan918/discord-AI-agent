import os

from dotenv import load_dotenv

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

load_dotenv(os.path.join(BASE_DIR, ".env"))

TOKEN = os.getenv("BOT_TOKEN")
MISTRAL_API_KEY = os.getenv("API_KEY")

# 數據文件路徑
DATA_FILES = {
    "discord_agent_data": os.path.join(DATA_DIR, "discord_agent_data.json"),
    # 只留下discord ai agent data
}
