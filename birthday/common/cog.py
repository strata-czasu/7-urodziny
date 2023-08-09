from discord.ext import commands

from .bot import Bot


class Cog(commands.Cog):
    bot: Bot

    def __init__(self, bot: Bot) -> None:
        self.bot = bot


class GroupCog(commands.GroupCog, metaclass=commands.CogMeta):
    bot: Bot

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        super().__init__()
