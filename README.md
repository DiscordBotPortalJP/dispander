# dispander
Discord Message URL Expander

# 使い方

## extensionとして使用する場合

load_extensionで読み込んでください

```python
from discord.ext import commands

bot = commands.Bot(command_prefix='/')
bot.load_extension('dispander')
bot.run(token)
```

## 関数として使用する場合

on_message内のどこかで実行してください

```python
import discord
from dispander import dispand

client = discord.client()

@client.event
async def on_message(message):
    if message.author.bot:
        return
    await dispand(message)

client.run(token)
```
