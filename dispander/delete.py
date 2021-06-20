from typing import Optional
from dispander.constants import regex_discord_message_url
from dispander.constants import regex_extra_url
from dispander.constants import DELETE_REACTION_EMOJI
import re
import discord


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
