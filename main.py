# 可以自行修改 這邊提供可用範例
import asyncio
import logging
import os

import discord
from discord.ext import commands

# 匯入日誌工具
from core.utils import log

# 建立 Logger
LOGGER = log.add_logg(
    name="Main",
    level=logging.INFO,
    color="cyan"
)

# 初始化 Bot 實例
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    LOGGER.info(f"Logged in as {bot.user.name} (ID: {bot.user.id})")

    # 同步 App Commands (Tree 指令)
    try:
        synced = await bot.tree.sync()
        LOGGER.info(f"成功同步 {len(synced)} 個應用程式指令 (Slash Commands)")
    except Exception:
        LOGGER.error("同步應用程式指令失敗", exc_info=True)


async def load_extensions():
    """載入所有 Bot Cogs 模組"""
    extension = "core.cogs.discord_agent.agent"
    try:
        await bot.load_extension(extension)
        LOGGER.info(f"Successfully loaded extension: {extension}")
    except Exception:
        LOGGER.error(f"Failed to load extension: {extension}", exc_info=True)


async def main():
    # 改成你自己的 Token
    token = None

    if not token:
        LOGGER.critical("請設定你的 Discord token 並替換 main.py:47")
        os.startfile(r"https://discord.com/developers/applications")
        return

    # 載入 Extensions
    await load_extensions()

    try:
        await bot.start(token)
    except discord.LoginFailure:
        LOGGER.critical("Discord 登入失敗：無效的 Token。", exc_info=True)
    except Exception:
        LOGGER.error("Bot 執行期間發生未預期錯誤", exc_info=True)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        LOGGER.info("Bot 已手動停止。")
