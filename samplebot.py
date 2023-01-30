import discord
from discord.ext import commands
from os import getenv


class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix='$',
            help_command=None,
            intents=discord.Intents.all(),
            application_id=getenv('APPLICATION_ID'),
        )

    async def setup_hook(self):
        await self.load_extension('dispander')


def main():
    MyBot().run(getenv('DISCORD_BOT_TOKEN'))


if __name__ == '__main__':
    main()
