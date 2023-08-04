from discord import Guild, Interaction, Member, app_commands

from birthday.common import Bot, Cog
from birthday.common.bot import Bot
from birthday.models import Profile


@app_commands.guild_only()
class Users(Cog):
    @app_commands.command(name="punkty")  # type: ignore[arg-type]
    async def points(self, itx: Interaction, member: Member | None = None):
        """Sprawdź ile ktoś ma punktów"""

        if member is None:
            assert isinstance(itx.user, Member)
            member = itx.user
            profile = await Profile.get_for(member.id, member.guild.id)
            return await itx.response.send_message(f"Masz {profile.points} pkt")

        profile = await Profile.get_for(member.id, member.guild.id)
        await itx.response.send_message(f"{member.mention} ma {profile.points} pkt")

    @app_commands.command(name="punkty-top")  # type: ignore[arg-type]
    async def points_top(self, itx: Interaction, amount: int = 10):
        """Sprawdź osoby z największą ilością punktów"""

        assert isinstance(itx.guild, Guild)
        top_profiles = (
            await Profile.objects.filter(guild_id=itx.guild.id)
            .order_by("-points")
            .limit(amount)
            .all()
        )
        top_string = "\n".join(
            f"{profile.points} - <@{profile.user_id}>" for profile in top_profiles
        )
        await itx.response.send_message(f"Top {amount} użytkowników:\n{top_string}")

    @app_commands.command(name="punkty-dodaj")  # type: ignore[arg-type]
    @app_commands.default_permissions(administrator=True)
    async def points_add(self, itx: Interaction, member: Member, amount: int):
        """Dodaj lub odejmij komuś punkty"""

        if amount == 0:
            return await itx.response.send_message(
                f"Wybierz więcej niż 0 punktów!", ephemeral=True
            )

        profile = await Profile.get_for(member.id, member.guild.id)
        profile.points += amount
        await profile.update()

        await itx.response.send_message(
            f"Dodano {amount} pkt {member.mention}, ma teraz {profile.points} pkt"
        )


async def setup(bot: Bot) -> None:
    await bot.add_cog(Users(bot))
