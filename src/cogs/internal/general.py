from collections import namedtuple
from time import time

from discord import Embed
from discord.ext import commands

from src.internal.bot import Bot
from src.internal.cog import Cog
from src.internal.context import Context

Result = namedtuple("Result", ["result", "time"])


class General(Cog):
    """A cog of general bot commands."""

    def __init__(self, bot: Bot):
        self.bot = bot

    @staticmethod
    async def timed_coro(coro) -> Result:
        ts = time()
        res = await coro
        return Result(res, round((time() - ts) * 1000, 2))

    @commands.command(name="ping")
    async def ping(self, ctx: Context):
        """Get the bot's API ping and websocket latency."""

        m_send = await self.timed_coro(ctx.send("Testing ping..."))
        m_edit = await self.timed_coro(m_send.result.edit(content="Edit test."))
        m_delete = await self.timed_coro(m_send.result.delete())

        embed = Embed(
            title="Bot Ping",
            timestamp=ctx.message.created_at,
            colour=0x87CEEB,
        )

        embed.add_field(name="API Send", value=f"{m_send.time}ms")
        embed.add_field(name="API Edit", value=f"{m_edit.time}ms")
        embed.add_field(name="API Delete", value=f"{m_delete.time}ms")
        embed.add_field(
            name="WS Latency", value=f"{round(self.bot.latency * 1000, 2)}ms"
        )

        await ctx.reply(embed=embed)


def setup(bot: Bot):
    bot.add_cog(General(bot))
