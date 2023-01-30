import os
import re
from typing import Optional
import discord
from discord.embeds import EmptyEmbed

regex_discord_message_url = (
    '(?!<)https://(ptb.|canary.)?discord(app)?.com/channels/'
    '(?P<guild>[0-9]{17,20})/(?P<channel>[0-9]{17,20})/(?P<message>[0-9]{17,20})(?!>)'
)
regex_extra_url = (
    r'\?base_aid=(?P<base_author_id>[0-9]{17,20})'
    '&aid=(?P<author_id>[0-9]{17,20})'
    '&extra=(?P<extra_messages>(|[0-9,]+))'
)
DELETE_REACTION_EMOJI = os.environ.get("DELETE_REACTION_EMOJI", "\U0001f5d1")


def compose_embed(message):
    embed = discord.Embed(
        description=message.content,
        timestamp=message.created_at,
    )
    embed.set_author(
        name=message.author.display_name,
        icon_url=message.author.avatar.url,
        url=message.jump_url
    )
    embed.set_footer(
        text=message.channel.name,
        icon_url=message.guild.icon.url,
    )
    if message.attachments and message.attachments[0].proxy_url:
        embed.set_image(
            url=message.attachments[0].proxy_url
        )
    return embed


async def dispand(message):
    messages = await extract_message(message)
    for m in messages:
        sent_messages = []

        if m.content or m.attachments:
            sent_message = await message.channel.send(embed=compose_embed(m))
            sent_messages.append(sent_message)
        # Send the second and subsequent attachments with embed (named 'embed') respectively:
        for attachment in m.attachments[1:]:
            embed = discord.Embed()
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
        main_embed = main_message.embeds[0]
        await main_message.add_reaction(DELETE_REACTION_EMOJI)
        if hasattr(main_embed.author.icon, "url"):
            icon_url = main_embed.author.icon.url
        else:
            icon_url = EmptyEmbed
        main_embed.set_author(
            name=getattr(main_embed.author, "name", None),
            icon_url=icon_url,
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
    channel = guild.get_channel_or_thread(channel_id)
    if channel is None:
        channel = await guild.fetch_channel(channel_id)
    message = await channel.fetch_message(message_id)
    return message


async def delete_dispand(bot: discord.Client,
                         *,
                         payload: Optional[discord.RawReactionActionEvent] = None,
                         reaction: Optional[discord.Reaction] = None,
                         user: Optional[discord.User] = None):
    if payload is not None:
        # when on_raw_reaction_add event
        if str(payload.emoji) != DELETE_REACTION_EMOJI:
            return
        if payload.user_id == bot.user.id:
            return

        channel = bot.get_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        await _delete_dispand(bot, message, payload.user_id)
    elif reaction is not None:
        # when on_reaction_add event
        if str(reaction.emoji) != DELETE_REACTION_EMOJI:
            return
        if user.id == bot.user.id:
            return
        await _delete_dispand(bot, reaction.message, user.id)
    else:
        raise ValueError("payload or reaction must be setted")


async def _delete_dispand(bot: discord.Client, message: discord.Message, operator_id: int):
    if message.author.id != bot.user.id:
        return
    elif not message.embeds:
        return

    embed = message.embeds[0]
    if getattr(embed.author, "url", None) is None:
        return
    data = from_jump_url(embed.author.url)
    if not (data["base_author_id"] == operator_id or data["author_id"] == operator_id):
        return
    await message.delete()
    for message_id in data["extra_messages"]:
        extra_message = await message.channel.fetch_message(message_id)
        if extra_message is not None:
            await extra_message.delete()


def make_jump_url(base_message, dispand_message, extra_messages):
    """
    make jump url which include more information
    :param base_message: メッセージリンクが貼られていたメッセージ
    :param dispand_message: 展開中のメッセージ
    :param extra_messages: 展開する際にでた二つ目以降のメッセージ(e.g. 画像やembed)
    :return: 混入が完了したメッセージリンク
    """
    # base_aid: メッセージリンクで飛べる最初のメッセージの送信者のid
    # aid: メッセージリンクを送信したユーザーのid
    return "{0.jump_url}?base_aid={1.id}&aid={2.id}&extra={3}".format(
        dispand_message,
        dispand_message.author,
        base_message.author,
        ",".join([str(i.id) for i in extra_messages])
    )


def from_jump_url(url):
    """
    メッセージリンクから情報を取得します。
    :param url: メッセージリンク
    :return: dict
    """
    base_url_match = re.match(regex_discord_message_url + regex_extra_url, url)
    data = base_url_match.groupdict()
    return {
        "base_author_id": int(data["base_author_id"]),
        "author_id": int(data["author_id"]),
        "extra_messages": [int(_id) for _id in data["extra_messages"].split(",")] if data["extra_messages"] else []
    }
