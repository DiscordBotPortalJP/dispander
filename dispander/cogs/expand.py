import discord
from discord.ext import commands
from dispander.utils import dispand
from dispander.utils import delete_dispand


class ExpandDiscordMessageFromUrlCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        await dispand(message)

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        await delete_dispand(self.bot, payload=payload)
