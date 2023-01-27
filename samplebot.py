import discord
from discord.ext import commands
import os
import asyncio

bot = commands.Bot(command_prefix='/', intents=discord.Intents().all())


async def main():
    async with bot:
        await bot.load_extension('dispander')
        await bot.start(os.getenv('DISCORD_BOT_TOKEN'))


if __name__ == '__main__':
    asyncio.run(main())
