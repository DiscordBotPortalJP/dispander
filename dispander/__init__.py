from dispander.cogs.expand import ExpandDiscordMessageFromUrlCog


async def setup(bot):
    await bot.add_cog(ExpandDiscordMessageFromUrlCog(bot))
