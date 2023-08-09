import discord
from discord import Guild
from discord.ext import commands
from discord.ext.commands import Context, Greedy

from birthday.common import Bot, Cog


@commands.is_owner()
class Management(Cog):
    @commands.command(name="reload", aliases=["r"])
    async def reload(self, ctx: Context):
        """Reload all loaded extensions"""

        async with ctx.typing():
            await self.bot.reload_extensions()

            await ctx.send("Reloaded extensions")

    @commands.group(name="sync", invoke_without_command=True)
    @commands.guild_only()
    async def sync(self, ctx: Context):
        """Sync global commands to the current guild"""

        assert isinstance(ctx.guild, Guild)
        async with ctx.typing():
            self.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await self.bot.tree.sync(guild=ctx.guild)

            await ctx.send(f"Synced {len(synced)} command(s) to this guild")

    @sync.command(name="global")  # type: ignore[arg-type]
    async def sync_global(self, ctx: Context):
        """Sync global commands"""

        async with ctx.typing():
            synced = await self.bot.tree.sync()

            await ctx.send(f"Synced {len(synced)} command(s) globally")

    @sync.command(name="guild", aliases=["guilds"])  # type: ignore[arg-type]
    @commands.guild_only()
    async def sync_guild(self, ctx: Context, guilds: Greedy[Guild]):
        """Sync guild commands"""

        if len(guilds) == 0:
            assert isinstance(ctx.guild, Guild)
            guilds.append(ctx.guild)

        synced_guilds = 0
        synced_commands = 0

        async with ctx.typing():
            for guild in guilds:
                try:
                    synced = await self.bot.tree.sync(guild=guild)
                    synced_guilds += 1
                    synced_commands += len(synced)
                except discord.HTTPException:
                    pass

            await ctx.send(
                f"Synced {synced_commands} command(s) to {synced_guilds} guild(s)"
            )

    @commands.group(name="clear")
    async def clear(self, _: Context):
        ...

    @clear.command(name="global")  # type: ignore[arg-type]
    async def clear_global(self, ctx: Context):
        """Clear global commands"""

        async with ctx.typing():
            self.bot.tree.clear_commands(guild=None)
            await self.bot.tree.sync()

            await ctx.send("Cleared command(s) globally")

    @clear.command(name="guild", aliases=["guilds"])  # type: ignore[arg-type]
    @commands.guild_only()
    async def clear_guild(self, ctx: Context, guilds: Greedy[Guild]):
        """Clear guild commands"""

        if len(guilds) == 0:
            assert isinstance(ctx.guild, Guild)
            guilds.append(ctx.guild)

        cleared_guilds = 0

        async with ctx.typing():
            for guild in guilds:
                try:
                    self.bot.tree.clear_commands(guild=guild)
                    await self.bot.tree.sync(guild=guild)
                    cleared_guilds += 1
                except discord.HTTPException:
                    pass

            await ctx.send(f"Cleared commands from {cleared_guilds} guild(s)")

    @commands.command(name="rs")
    async def reload_and_sync(self, ctx: Context):
        """Reload all loaded extensions and sync global commands to the current guild"""

        await self.reload(ctx)
        await self.sync(ctx)


async def setup(bot: Bot) -> None:
    await bot.add_cog(Management(bot))
