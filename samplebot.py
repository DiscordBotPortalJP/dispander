from discord.ext import commands
import os

if __name__ == '__main__':
    bot = commands.Bot(command_prefix='/')
    bot.allow_external_links = True
    bot.load_extension('dispander')
    bot.run(os.getenv('DISCORD_BOT_TOKEN'))
