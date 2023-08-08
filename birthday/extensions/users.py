from discord import Embed, Guild, Interaction, Member, User, app_commands

from birthday.common import Bot, Cog
from birthday.common.bot import Bot
from birthday.common.views import Paginator, UserSelectView
from birthday.constants import EMBED_COLOR
from birthday.models import Profile


@app_commands.guild_only()
class Users(Cog):
    @app_commands.command(name="dukaty")  # type: ignore[arg-type]
    @app_commands.rename(member="użytkownik")
    @app_commands.describe(
        member="Użytkownik, którego stan konta chcesz sprawdzić (domyślnie Twój)"
    )
    async def points(self, itx: Interaction, member: Member | None = None):
        """Sprawdź ile ktoś ma dukatów"""

        if member is None:
            assert isinstance(itx.user, Member)
            member = itx.user
            profile = await Profile.get_for(member.id, member.guild.id)
            description = f"Twój stan konta: **{profile.points}** 🪙"
        else:
            profile = await Profile.get_for(member.id, member.guild.id)
            description = f"Stan konta {member.mention}: **{profile.points}** 🪙"

        embed = Embed(
            title="Stan konta",
            description=description,
            color=EMBED_COLOR,
        )
        await itx.response.send_message(embed=embed)

    @app_commands.command(name="dukaty-ranking")  # type: ignore[arg-type]
    async def points_ranking(self, itx: Interaction):
        """Sprawdź ranking osób z największą ilością dukatów"""

        assert isinstance(itx.guild, Guild)
        top_profiles = (
            await Profile.objects.filter(guild_id=itx.guild.id)
            .order_by("-points")
            .all()
        )

        def page_formatter(items: list[Profile], start_position: int) -> str:
            return "\n".join(
                f"{i}. <@{profile.user_id}> - **{profile.points}** 🪙"
                for i, profile in enumerate(items, start_position)
            )

        view = Paginator(itx, "Ranking dukatowy 🪙", top_profiles, page_formatter)
        await itx.response.send_message(embed=view.get_embed(), view=view)

    @app_commands.command(name="dukaty-dodaj")  # type: ignore[arg-type]
    @app_commands.rename(member="użytkownik", amount="ilość")
    @app_commands.describe(
        member="Użytkownik, któremu chcesz dodać dukaty",
        amount="Ilość dukatów (może być ujemna)",
    )
    @app_commands.default_permissions(administrator=True)
    async def points_add(self, itx: Interaction, member: Member, amount: int):
        """Dodaj lub odejmij komuś dukaty"""

        if amount == 0:
            return await itx.response.send_message(
                f"Wybierz więcej niż 0 dukatów!", ephemeral=True
            )

        profile = await Profile.get_for(member.id, member.guild.id)
        profile.points += amount
        await profile.update()

        embed = Embed(
            title="Dukaty wleciały na konto!",
            description=f"Na konto <@{member.id}> wpłynęło **{amount}** 🪙",
            color=EMBED_COLOR,
        )
        await itx.response.send_message(embed=embed)

    @app_commands.command(name="dukaty-dodaj-wiele")  # type: ignore[arg-type]
    @app_commands.rename(amount="ilość")
    @app_commands.describe(amount="Ilość dukatów (może być ujemna)")
    @app_commands.default_permissions(administrator=True)
    async def points_add_multiple(self, itx: Interaction, amount: int):
        """Dodaj lub odejmij dukaty wielu użytkownikom jednocześnie"""

        if amount == 0:
            return await itx.response.send_message(
                f"Wybierz więcej niż 0 dukatów!", ephemeral=True
            )

        async def user_select_callback(
            itx: Interaction, users: list[Member | User]
        ) -> None:
            assert isinstance(itx.guild, Guild)
            updated_profiles: list[Profile] = []
            for user in users:
                profile = await Profile.get_for(user.id, itx.guild.id)
                profile.points += amount
                updated_profiles.append(profile)

            await Profile.objects.bulk_update(updated_profiles, ["points"])
            await itx.response.send_message(
                f"Na konta wybranych osób wypłynęło **{amount}** 🪙"
            )

        view = UserSelectView(itx, user_select_callback)
        await itx.response.send_message(
            f"Wybierz użytkowników, którym chcesz dodać **{amount}** 🪙",
            view=view,
            ephemeral=True,
        )


async def setup(bot: Bot) -> None:
    await bot.add_cog(Users(bot))
