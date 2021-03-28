from asyncpg import create_pool
from traceback import format_exc
from os import getenv, walk

from loguru import logger


class Database:
    """A database interface for the bot to connect to Postgres."""

    def __init__(self):
        self.guilds = {}

    async def setup(self):
        logger.info("Setting up database...")
        self.pool = await create_pool(
            host=getenv("DB_HOST", "127.0.0.1"),
            port=getenv("DB_PORT", 5432),
            database=getenv("DB_DATABASE"),
            user=getenv("DB_USER", "root"),
            password=getenv("DB_PASS", "password"),
        )
        logger.info("Database setup complete.")

        await self.automigrate()

    async def automigrate(self):
        allow = getenv("AUTOMIGRATE", "false")

        if allow != "true":
            logger.info("Automigrating is disabled, skipping migration attempt.")
            return

        try:
            migration = await self.fetchrow("SELECT id FROM Migrations ORDER BY id DESC LIMIT 1;")
        except Exception as e:
            print(e)
            migration = None

        migration = migration["id"] if migration else 0

        fs = []

        for root, dirs, files in walk("./src/data/"):
            for file in files:
                mnum = int(file[0:4])
                fs.append((mnum, file))

        fs.sort()
        fs = [f for f in fs if f[0] > migration]

        if not fs:
            return

        logger.info("Running automigrate...")

        for file in fs:
            res = await self.run_migration(file[1], file[0])
            if not res:
                break

        logger.info("Finished automigrate.")

    async def run_migration(self, filename: str, num: int):
        logger.info(f"Running migration {filename}...")
        try:
            with open(f"./src/data/{filename}") as f:
                await self.execute(f.read())
            await self.execute("INSERT INTO Migrations VALUES ($1);", num)
        except Exception as e:
            logger.error(f"Failed to run migration {filename}: {format_exc()}")
            return False
        else:
            logger.info(f"Successfully ran migration {filename}.")
            return True

    async def execute(self, query: str, *args):
        async with self.pool.acquire() as conn:
            await conn.execute(query, *args)

    async def fetchrow(self, query: str, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetchrow(query, *args)

    async def fetch(self, query: str, *args):
        async with self.pool.acquire() as conn:
            return await conn.fetch(query, *args)
