# 可以自行修改 這邊提供可用範例
import asyncio
import logging
import os
import sys

import config
import discord

# 匯入日誌工具
from core.utils import log
from discord.ext import commands

# 建立 Logger
LOGGER = log.add_logg(
    name="Main",
    level=logging.INFO,
    color="cyan"
)

def update_token(token):
    file_path = '.env'

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        lines = []

    new_first_line = f"BOT_TOKEN={token}\n"

    if lines:
        lines[0] = new_first_line
    else:
        lines = [new_first_line]

    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(lines)

# 初始化 Bot 實例
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    LOGGER.info(f"Logged in as {bot.user.name} (ID: {bot.user.id})")
    LOGGER.info(f"Invite with: https://discord.com/oauth2/authorize?client_id={bot.user.id}&permissions=8&integration_type=0&scope=bot")

    # 同步 App Commands (Tree 指令)
    try:
        synced = await bot.tree.sync()
        LOGGER.info(f"成功同步 {len(synced)} 個應用程式指令 (Slash Commands)")
    except Exception:
        LOGGER.error("同步應用程式指令失敗", exc_info=True)


async def load_extensions():
    """載入所有 Bot Cogs 模組"""
    extensions = [
        "core.cogs.discord_agent.agent",
        "core.cogs.stop.stop",
    ]

    for ext in extensions:
        try:
            await bot.load_extension(ext)
            LOGGER.info(f"Successfully loaded extension: {ext}")
        except Exception:
            LOGGER.error(f"Failed to load extension: {ext}", exc_info=True)


async def main():
    # 改成你自己的 Token
    token = config.TOKEN

    if token == "YOUR_BOT-TOKEN_HERE":
        LOGGER.critical("請取得你的 Bot token")
        await asyncio.sleep(2)
        os.startfile(r"https://discord.com/developers/applications")
        await asyncio.sleep(5)
        update_token(input("請在此輸入你的 Bot token："))
        LOGGER.info("BOT TOKEN 設定完成 即將重新啟動")
        await asyncio.sleep(3)

        os.startfile(r"run.bat")
        sys.exit(2)

    # 載入 Extensions
    await load_extensions()

    try:
        await bot.start(token)
    except discord.LoginFailure:
        LOGGER.critical("Discord 登入失敗：無效的 Token。", exc_info=True)
    except discord.errors.PrivilegedIntentsRequired:
        LOGGER.critical(
            "Bot 需要開啟 intents 才能運行\n"
            "請進入到你的應用程式設定頁面，開啟 intents 並重新啟動 Bot"
        )

        await asyncio.sleep(6)
        os.startfile(
            "https://discord.com/developers/applications"
        )

    except Exception:
        LOGGER.error("Bot 執行期間發生未預期錯誤", exc_info=True)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        LOGGER.info("Bot 已手動停止。")
