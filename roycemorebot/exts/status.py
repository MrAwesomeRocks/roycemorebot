import asyncio
import logging
from datetime import datetime

from discord import Colour, Embed
from discord.ext import commands
from discord.ext.commands.errors import CommandError, MissingAnyRole, NoPrivateMessage

from roycemorebot.constants import Channels, Emoji, Roles

PRECISION = 3

log = logging.getLogger(__name__)


class Status(commands.Cog):
    """Status commands for the bot."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx: commands.Context) -> None:
        """Send the latency of the bot."""
        raw_bot_latency = (
            datetime.utcnow() - ctx.message.created_at
        ).total_seconds() * 1000
        bot_latency = f"{raw_bot_latency:.{PRECISION}f} ms"
        raw_api_latency = self.bot.latency * 1000
        api_latency = f"{raw_api_latency:.{PRECISION}f} ms"

        if raw_bot_latency <= 100 and raw_api_latency <= 100:
            embed = Embed(title="Pong!", colour=Colour.green())
        elif raw_bot_latency <= 250 and raw_api_latency <= 250:
            embed = Embed(title="Pong!", colour=Colour.orange())
        else:
            embed = Embed(title="Pong!", colour=Colour.red())

        embed.add_field(name="Bot latency:", value=bot_latency, inline=False)
        embed.add_field(name="Discord API Latency:", value=api_latency, inline=False)

        await ctx.send(embed=embed)

    @commands.guild_only()
    @commands.has_any_role(Roles.bot_team_role, Roles.admin_role)
    @commands.command()
    async def restart(self, ctx: commands.Context, delay: int = 0) -> None:
        """Restart the bot after a certain delay (in seconds)."""
        if delay != 0:
            await ctx.send(f"{Emoji.ok} Restarting in {delay} seconds.")
        await asyncio.sleep(delay)

        bot_log_channel = self.bot.get_channel(Channels.bot_log)
        await bot_log_channel.send(f"{Emoji.warning} Restarting!")

        log.info(
            f"Restarting at the request of {ctx.message.author.name}#{ctx.message.author.discriminator}"  # noqa: B950
        )
        await self.bot.logout()
        # restarted by PM2 now

    @restart.error
    async def restart_error(self, ctx: commands.Context, error: CommandError) -> None:
        """Error handler for the restart command."""
        if isinstance(error, MissingAnyRole):
            await ctx.send(
                f"""{Emoji.no} You do not have permissions to restart the bot. Ping `@Bot Team` if the bot isn't working properly."""  # noqa: B950
            )
        elif isinstance(error, NoPrivateMessage):
            await ctx.send(f"{Emoji.no} You must be in a server to restart the bot.")


def setup(bot: commands.Bot) -> None:
    """Add the status cog."""
    bot.add_cog(Status(bot))
