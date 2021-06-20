from discord import Embed
from discord.ext import commands
from dispander.delete import delete_dispand
from dispander.delete import make_jump_url
from dispander.constants import regex_discord_message_url
from dispander.constants import DELETE_REACTION_EMOJI
from discord.embeds import EmptyEmbed
import re
import discord


class ExpandDiscordMessageUrl(commands.Cog):
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


async def dispand(message):
    messages = await extract_message(message)
    for m in messages:
        sent_messages = []

        if m.content or m.attachments:
            sent_message = await message.channel.send(embed=compose_embed(m))
            sent_messages.append(sent_message)
        # Send the second and subsequent attachments with embed (named 'embed') respectively:
        for attachment in m.attachments[1:]:
            embed = Embed()
            embed.set_image(
                url=attachment.proxy_url
            )
            sent_attachment_message = await message.channel.send(embed=embed)
            sent_messages.append(sent_attachment_message)

        for embed in m.embeds:
            sent_embed_message = await message.channel.send(embed=embed)
            sent_messages.append(sent_embed_message)

        # 一番先頭のメッセージにゴミ箱のリアクションをつける
        main_message = sent_messages.pop(0)
        await main_message.add_reaction(DELETE_REACTION_EMOJI)
        main_embed = main_message.embeds[0]
        main_embed.set_author(
            name=getattr(main_embed.author, "name", EmptyEmbed),
            icon_url=getattr(main_embed.author, "icon_url", EmptyEmbed),
            url=make_jump_url(message, m, sent_messages)
        )
        await main_message.edit(embed=main_embed)


async def extract_message(message):
    messages = []
    for ids in re.finditer(regex_discord_message_url, message.content):
        if message.guild.id != int(ids['guild']):
            continue
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
        url=message.jump_url
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
