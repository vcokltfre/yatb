from datetime import datetime

from discord import Embed
from discord.ext import commands
from discord.ext.commands import CommandError, errors
from loguru import logger

from src.internal.bot import Bot
from src.internal.cog import Cog
from src.internal.context import Context


class ErrorHandler(Cog):
    """A custom error handling cog."""

    def __init__(self, bot: Bot):
        self.bot = bot

    def get_embed(self, title: str, description: str):
        embed = Embed(
            title=title,
            description=str(description),
            colour=0xFF0000,
            timestamp=datetime.utcnow(),
        )

        embed.set_footer(
            text=str(self.bot.user.name), icon_url=str(self.bot.user.avatar_url)
        )

        return embed

    @staticmethod
    def get_help(ctx: Context):
        """Return a prepare help command."""

        if command := ctx.command:
            return ctx.send_help(command)

        return ctx.send_help()

    @commands.Cog.listener()
    async def on_command_error(self, ctx: Context, error: CommandError):
        """Handle command errors."""

        command = ctx.command

        if isinstance(error, errors.CommandNotFound):
            logger.warning(f"Command not found: {command}")
            return
        elif isinstance(error, errors.UserInputError):
            await self.user_input_error(ctx, error)
        elif isinstance(error, errors.CheckFailure):
            await self.check_failure(ctx, error)
        elif isinstance(error, errors.CommandOnCooldown):
            embed = self.get_embed(
                "Command on cooldown",
                f"This command is on cooldown. Try again in {round(error.retry_after, 2)}s",
            )
            await ctx.send(embed=embed)
        else:
            embed = self.get_embed("Unexpected internal error", f"```py\n{error}\n```")
            await ctx.send(embed=embed)

        logger.warning(
            f"Error in command {command} invoked by {ctx.message.author}\n{error.__class__.__name__}: {error}"
        )

    async def user_input_error(self, ctx: Context, error: errors.UserInputError):
        """Handle a user input error."""

        help_command = self.get_help(ctx)

        if isinstance(error, errors.MissingRequiredArgument):
            embed = self.get_embed("Missing required argument", error.param.name)
            await ctx.send(embed=embed)
            await help_command
        elif isinstance(error, errors.TooManyArguments):
            embed = self.get_embed("Too many arguments", str(error))
            await ctx.send(embed=embed)
            await help_command
        elif isinstance(error, errors.BadArgument):
            embed = self.get_embed("Bad argument", str(error))
            await ctx.send(embed=embed)
            await help_command
        elif isinstance(error, errors.BadUnionArgument):
            embed = self.get_embed("Bad argument", f"{error}\n{error.errors[-1]}")
            await ctx.send(embed=embed)
            await help_command
        elif isinstance(error, errors.ArgumentParsingError):
            embed = self.get_embed("Argument parsing error", str(error))
            await ctx.send(embed=embed)
            help_command.close()
        else:
            embed = self.get_embed(
                "Input error",
                "Something about your input seems off. Check the arguments and try again.",
            )
            await ctx.send(embed=embed)
            await help_command

    @staticmethod
    async def check_failure(ctx: Context, e: errors.CheckFailure) -> None:
        """Handle a command check failure."""

        bot_missing_errors = (
            errors.BotMissingPermissions,
            errors.BotMissingRole,
            errors.BotMissingAnyRole,
        )

        if isinstance(e, bot_missing_errors):
            ctx.bot.stats.incr("errors.bot_permission_error")
            await ctx.send(
                "Sorry, it looks like I don't have the permissions or roles I need to do that."
            )
        elif isinstance(e, errors.NoPrivateMessage):
            await ctx.send(e)


def setup(bot: Bot):
    bot.add_cog(ErrorHandler(bot))
