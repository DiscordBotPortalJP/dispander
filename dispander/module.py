from discord import Embed
from discord.ext import commands
import re

regex_discord_message_url = (
    'https://(canary.)?discordapp.com/channels/'
    '(?P<guild>[0-9]{18})/(?P<channel>[0-9]{18})/(?P<message>[0-9]{18})'
)


class ExpandDiscordMessageUrl(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.allow_external_links = getattr(bot, 'allow_external_links', False) is True

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        await dispand(message, self.allow_external_links)


async def dispand(message, allow_external_links=False):
    messages = await extract_messsages(message, allow_external_links)
    for m in messages:
        if message.content:
            await message.channel.send(embed=compose_embed(m))
        for embed in m.embeds:
            await message.channel.send(embed=embed)


async def extract_messsages(message, allow_external_links=False):
    messages = []
    for ids in re.finditer(regex_discord_message_url, message.content):
        if not allow_external_links and message.guild.id != int(ids['guild']):
            return
        fetched_message = await fetch_message_from_id(
            guild=message.guild,
            channel_id=int(ids['channel']),
            message_id=int(ids['message']),
        )
        messages.append(fetched_message)
    return messages


async def fetch_message_from_id(guild, channel_id, message_id):
    channel = guild.get_channel(channel_id)
    message = await channel.fetch_message(message_id)
    return message


def compose_embed(message):
    embed = Embed(
        description=message.content,
        timestamp=message.created_at,
    )
    embed.set_author(
        name=message.author.display_name,
        icon_url=message.author.avatar_url,
    )
    embed.set_footer(
        text=message.channel.name,
        icon_url=message.guild.icon_url,
    )
    if message.attachments and message.attachments[0].proxy_url:
        embed.set_image(
            url=message.attachments[0].proxy_url
        )
    return embed


def setup(bot):
    bot.add_cog(ExpandDiscordMessageUrl(bot))
