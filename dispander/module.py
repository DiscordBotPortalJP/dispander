from discord import Embed
from discord.ext import commands
import re


class ExpandDiscordMessageUrl(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.url_discord_message = (
            'https://(canary.)?discordapp.com/channels/'
            '(?P<guild>[0-9]{18})/(?P<channel>[0-9]{18})/(?P<message>[0-9]{18})'
        )

    @commands.Cog.listener()
    async def on_message(self, message):
        for ids in re.finditer(self.url_discord_message, message.content):
            if message.guild.id == int(ids['guild']):
                target_message = await fetch_message_from_id(
                    guild=message.guild,
                    channel_id=int(ids['channel']),
                    message_id=int(ids['message']),
                )
                embed = compose_embed(target_message)
            else:
                embed = Embed(title='404')
            await message.channel.send(embed=embed)


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
