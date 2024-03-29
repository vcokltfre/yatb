from os import getenv

from dotenv import load_dotenv

from src.internal.bot import Bot

load_dotenv()

bot = Bot()

bot.load_extensions(
    "jishaku",
    "src.cogs.internal.error_handler",
    "src.cogs.internal.general",
)

bot.run(getenv("TOKEN"))
