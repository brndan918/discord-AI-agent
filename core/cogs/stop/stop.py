import logging

import discord
from discord import app_commands
from discord.ext import commands

from core.utils import log

LOGGER = log.add_logg(
    name="stop bot (/stop)",
    level=logging.INFO,
    color="Magenta"
)

class ConfirmStopView(discord.ui.View):
    """二次確認按鈕 View"""

    def __init__(self, author_id: int):
        super().__init__(timeout=30)  # 30 秒未操作自動失效
        self.author_id = author_id

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # 防止其他人點擊按鈕
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "❌ 只有觸發指令的使用者才能操作此按鈕！", ephemeral=True
            )
            return False
        return True

    @discord.ui.button(label="確認關閉", style=discord.ButtonStyle.danger)
    async def confirm(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_message("🛑 機器人正在關閉中...", ephemeral=True)
        LOGGER.info(f"Bot shutdown initiated by {interaction.user} (ID: {interaction.user.id})")
        await interaction.client.close()

    @discord.ui.button(label="取消", style=discord.ButtonStyle.secondary)
    async def cancel(
        self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await interaction.response.send_message("✅ 已取消關閉操作。", ephemeral=True)
        self.stop()


class StopCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="stop", description="停止機器人")
    @app_commands.default_permissions(administrator=True)
    async def stop_bot(self, interaction: discord.Interaction):
        view = ConfirmStopView(author_id=interaction.user.id)
        await interaction.response.send_message(
            "⚠️ **確定要停止機器人嗎？",
            view=view,
            ephemeral=True,  # 設為僅指令發送者可見
        )


async def setup(bot: commands.Bot):
    await bot.add_cog(StopCog(bot))