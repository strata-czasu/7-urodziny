from birthday.common import Bot

from .cog import Map


async def setup(bot: Bot) -> None:
    await bot.add_cog(Map(bot))
