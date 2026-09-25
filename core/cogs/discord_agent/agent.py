import traceback

import discord
from discord import app_commands
from discord.ext import commands

from .setup import LOGGER, AgentSetupMixin, is_owner


@app_commands.guild_only()
class DiscordAgent(AgentSetupMixin, commands.GroupCog, name="agent", description="Discord AI agent（僅服主可用）"):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.init_agent()

    async def cog_load(self) -> None:
        await self.agent_load()

    async def cog_unload(self) -> None:
        await self.agent_unload()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """套用到 /agent 底下所有子指令：只有服主能用"""
        if is_owner(interaction):
            return True
        LOGGER.debug("非服主嘗試使用 /agent: %s", interaction.user.id)
        await interaction.response.send_message("❌ 只有服主可以使用 /agent 指令", ephemeral=True)
        return False

    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        if isinstance(error, app_commands.CheckFailure):
            return  # 已在 interaction_check 回覆過
        LOGGER.error("/agent 指令錯誤:\n%s", "".join(traceback.format_exception(error)))
        msg = "❌ 指令發生未預期的錯誤 請稍後再試"
        try:
            if interaction.response.is_done():
                await interaction.followup.send(msg, ephemeral=True)
            else:
                await interaction.response.send_message(msg, ephemeral=True)
        except discord.HTTPException:
            pass


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(DiscordAgent(bot))