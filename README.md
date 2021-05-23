# dispander (Discord Message URL Expander)
DiscordのメッセージURLを検知して展開する機能を追加する discord.py Bot拡張用ライブラリ

<img width="789" src="https://user-images.githubusercontent.com/11159059/70523586-bc7b8280-1b86-11ea-87f3-aa3dade6ba51.png">

# 使い方

`python3 -m pip install dispander`

## extensionとして使用する場合

load_extensionで読み込んでください

```python
from discord.ext import commands

bot = commands.Bot(command_prefix='/')
bot.load_extension('dispander')
bot.run(token)
```

## 関数として使用する場合

on_message内のどこかで実行してください。

展開したメッセージを消去する機能を使用するには`on_reaction_add`イベントもしくは`on_raw_reaction_add`イベントのどちらかでdelete_dispand関数を実行してください。
on_raw_reaction_addの場合はキーワード引数`payload`にRawReactionActionEventを、on_reaction_addの場合はキーワード引数`user`にUser、`reaction`にReactionを指定して下さい。

消去の際のリアクションを変更したい場合は環境変数`DELETE_REACTION_EMOJI`に絵文字を設定してください。

```python
import discord
from dispander import dispand, delete_dispand

client = discord.Client()

@client.event
async def on_message(message):
    if message.author.bot:
        return
    await dispand(message)


@client.event
async def on_raw_reaction_add(payload):
    await delete_dispand(client, payload=payload)


client.run(token)
```
