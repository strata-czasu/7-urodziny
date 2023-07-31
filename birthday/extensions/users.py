from collections import Counter, defaultdict

from discord import Interaction, Member, User, app_commands

from birthday.common import Bot, Cog
from birthday.common.bot import Bot


@app_commands.guild_only()
class Users(Cog):
    def __init__(self, bot: Bot) -> None:
        super().__init__(bot)
        # TODO: Replace with a db
        self.members: dict[int, int] = defaultdict(int)

    @app_commands.command(name="punkty")  # type: ignore[arg-type]
    async def points(self, itx: Interaction, member: Member | None = None):
        """Sprawdź ile ktoś ma punktów"""

        if member is None:
            points = self.members.get(itx.user.id, 0)
            return await itx.response.send_message(f"Masz {points} pkt")

        points = self.members.get(member.id, 0)
        await itx.response.send_message(f"{member.mention} ma {points} pkt")

    @app_commands.command(name="punkty-top")  # type: ignore[arg-type]
    async def points_top(self, itx: Interaction, amount: int = 10):
        """Sprawdź osoby z największą ilością punktów"""

        member_points = Counter(self.members)
        top_string = "\n".join(
            f"{points} - <@{member}>"
            for member, points in member_points.most_common(amount)
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

        self.members[member.id] += amount

        await itx.response.send_message(
            f"Dodano {amount} pkt {member.mention}, "
            f"ma teraz {self.members.get(member.id)} pkt"
        )


async def setup(bot: Bot) -> None:
    await bot.add_cog(Users(bot))
