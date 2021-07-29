import discord

if discord.version_info.major == 2:
    from dispander.module_v2 import *
else:
    from dispander.module import *
