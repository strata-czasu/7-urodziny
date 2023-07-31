from discord import Interaction, app_commands

from birthday.common import Bot, Cog


class Info(Cog):
    @app_commands.command()
    async def ping(self, itx: Interaction):
        """Ping Pong 🏓"""

        latency_ms = round(self.bot.latency * 1000)
        await itx.response.send_message(
            f"Pong! :ping_pong: \n\nWebsocket latency: {latency_ms}ms"
        )


async def setup(bot: Bot) -> None:
    await bot.add_cog(Info(bot))
