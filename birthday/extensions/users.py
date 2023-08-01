from discord import Interaction, Member, app_commands

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
            profile = await self._get_profile(itx.user)
            return await itx.response.send_message(f"Masz {profile.points} pkt")

        profile = await self._get_profile(member)
        await itx.response.send_message(f"{member.mention} ma {profile.points} pkt")

    @app_commands.command(name="punkty-top")  # type: ignore[arg-type]
    async def points_top(self, itx: Interaction, amount: int = 10):
        """Sprawdź osoby z największą ilością punktów"""

        top_profiles = await Profile.objects.order_by("-points").limit(amount).all()
        top_string = "\n".join(
            f"{profile.points} - <@{profile.user_id}>" for profile in top_profiles
        )
        await itx.response.send_message(f"Top {amount} użytkowników:\n{top_string}")

    @app_commands.command(name="punkty-dodaj")  # type: ignore[arg-type]
    @app_commands.default_permissions(administrator=True)
    async def points_add(self, itx: Interaction, amount: int, member: Member):
        """Dodaj lub odejmij komuś punkty"""

        if amount == 0:
            return await itx.response.send_message(
                f"Wybierz więcej niż 0 punktów!", ephemeral=True
            )

        profile = await self._get_profile(member)
        profile.points += amount
        await profile.update()

        await itx.response.send_message(
            f"Dodano {amount} pkt {member.mention}, ma teraz {profile.points} pkt"
        )

    @staticmethod
    async def _get_profile(member: Member) -> Profile:
        defaults = {"points": 0}
        profile, _ = await Profile.objects.get_or_create(
            defaults, user_id=member.id, guild_id=member.guild.id
        )
        return profile


async def setup(bot: Bot) -> None:
    await bot.add_cog(Users(bot))
