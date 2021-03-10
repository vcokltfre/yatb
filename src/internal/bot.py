from discord.ext import commands
from discord import Intents, Message

from loguru import logger
from traceback import format_exc

from .help import Help
from .context import Context

from src.utils.database import Database


class Bot(commands.Bot):
    """A subclass of commands.Bot with additional functionality."""

    def __init__(self, *args, **kwargs):
        logger.info("Starting up...")

        intents = Intents.all()

        super().__init__(
            command_prefix=self.get_prefix,
            intents=intents,
            help_command=Help(),
            *args,
            **kwargs
        )

        self.db: Database = Database()

    def load_extensions(self, *exts) -> None:
        """Load a given set of extensions."""

        logger.info(f"Starting loading {len(exts)} cogs...")

        success = 0

        for ext in exts:
            try:
                self.load_extension(ext)
            except:
                logger.error(f"Error while loading {ext}:\n{format_exc()}")
            else:
                logger.info(f"Successfully loaded cog {ext}.")
                success += 1

        logger.info(f"Cog loading finished. Success: {success}. Failed: {len(exts) - success}.")

    async def login(self, *args, **kwargs) -> None:
        """Create the database connection before login."""

        await self.db.setup()

        await super().login(*args, **kwargs)

    async def get_prefix(self, message: Message):
        """Get a dynamic prefix."""

        return "!"  # Implementation left to actual bot, rather than yatb

    async def get_context(self, message: Message):
        """Get the context with the custom context class."""

        return await super().get_context(message, cls=Context)
