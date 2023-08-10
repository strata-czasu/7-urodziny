import random
from collections import Counter
from datetime import datetime
from io import BytesIO

from discord import Embed, File, Guild, Interaction, Member, app_commands
from discord.app_commands import AppCommandError, CommandOnCooldown

from birthday.common import Cog
from birthday.common.bot import Bot
from birthday.common.views import Paginator
from birthday.constants import EMBED_COLOR
from birthday.extensions.map.views import MapImageView
from birthday.models import MapCompletion, MapSegment, Profile

from .map_image import MapImageGenerator


@app_commands.guild_only()
class Map(Cog):
    MAP_ELEMENT_COST = 150

    def __init__(self, bot: Bot) -> None:
        super().__init__(bot)
        self.map_image_generator = MapImageGenerator()

    @app_commands.command(name="mapa")  # type: ignore[arg-type]
    @app_commands.rename(member="użytkownik")
    @app_commands.describe(
        member="Użytkownik, którego mapę chcesz sprawdzić (domyślnie Twoją)"
    )
    @app_commands.checks.cooldown(1, 5)
    async def show_map(self, itx: Interaction, member: Member | None = None):
        """Sprawdź aktualny postęp na mapie"""

        if member is None:
            assert isinstance(itx.user, Member)
            member = itx.user

        await itx.response.defer()

        profile = await Profile.get_for(member.id, member.guild.id)
        existing_segments = await self._get_existing_segments(profile)

        view = MapImageView(
            itx,
            f"Mapa {member.display_name}",
            profile,
            existing_segments,
            self.map_image_generator,
        )
        embed = view.get_embed()
        file = view.get_map_image()

        if member is itx.user and view.can_buy_element():
            await itx.followup.send(embed=embed, file=file, view=view)
        else:
            await itx.followup.send(embed=embed, file=file)

    @show_map.error
    async def show_map_error(self, itx: Interaction, error: AppCommandError):
        if isinstance(error, CommandOnCooldown):
            return await itx.response.send_message(
                f"Zwolnij trochę! Spróbuj ponownie za **{error.retry_after:.0f}**s",
                ephemeral=True,
            )
        raise error

    @app_commands.command(name="mapa-kup")  # type: ignore[arg-type]
    async def buy_map_element(self, itx: Interaction):
        """Kup losową część mapy"""

        assert isinstance(itx.user, Member)
        profile = await Profile.get_for(itx.user.id, itx.user.guild.id)
        if profile.points < self.MAP_ELEMENT_COST:
            return await itx.response.send_message(
                f"Nie masz wystarczająco dukatów, potrzebujesz **{self.MAP_ELEMENT_COST}** 🪙",
                ephemeral=True,
            )

        existing_segments = await self._get_existing_segments(profile)
        available_segments = self._get_available_segments(existing_segments)
        if len(available_segments) == 0:
            return await itx.response.send_message(
                f"Masz już wszystkie części mapy!", ephemeral=True
            )

        segment = random.choice(available_segments)
        await MapSegment.objects.create(profile=profile, number=segment)
        profile.points -= self.MAP_ELEMENT_COST
        await profile.update()

        embed = Embed(
            title="Zakupiono część mapy!",
            description=f"Masz aktualnie **{len(existing_segments) + 1}/"
            f"{self.map_image_generator.SEGMENTS}** części mapy!",
            color=EMBED_COLOR,
        )
        await itx.response.send_message(embed=embed)
        await self._check_map_completion(itx, profile)

    @app_commands.command(name="mapa-kup-wszystko")  # type: ignore[arg-type]
    async def buy_all_map_elements(self, itx: Interaction):
        """Kup tyle elementów mapy, na ile Cię stać"""

        assert isinstance(itx.user, Member)
        profile = await Profile.get_for(itx.user.id, itx.user.guild.id)
        if profile.points < self.MAP_ELEMENT_COST:
            return await itx.response.send_message(
                f"Nie masz wystarczająco dukatów, potrzebujesz **{self.MAP_ELEMENT_COST}** 🪙",
                ephemeral=True,
            )

        existing_segments = await self._get_existing_segments(profile)
        available_segments = self._get_available_segments(existing_segments)
        if len(available_segments) == 0:
            return await itx.response.send_message(
                f"Masz już wszystkie części mapy!", ephemeral=True
            )

        segments_to_buy = min(
            profile.points // self.MAP_ELEMENT_COST,
            # Limit to the available segments
            len(available_segments),
        )
        segments = random.sample(available_segments, segments_to_buy)
        await MapSegment.objects.bulk_create(
            [MapSegment(profile=profile, number=segment) for segment in segments]
        )
        profile.points -= segments_to_buy * self.MAP_ELEMENT_COST
        await profile.update()

        embed = Embed(
            title=f"Zakupiono {segments_to_buy} część mapy!",
            description=f"Masz aktualnie **{len(existing_segments) + segments_to_buy}/"
            f"{self.map_image_generator.SEGMENTS}** części mapy!",
            color=EMBED_COLOR,
        )
        await itx.response.send_message(embed=embed)
        await self._check_map_completion(itx, profile)

    @app_commands.command(name="mapa-dodaj")  # type: ignore[arg-type]
    @app_commands.rename(member="użytkownik")
    @app_commands.describe(
        member="Użytkownik, któremu chcesz dodać element mapy",
        element="Element mapy, który chcesz dodać (domyślnie losowy)",
    )
    @app_commands.default_permissions(administrator=True)
    async def add_map_element(
        self, itx: Interaction, member: Member, element: int | None
    ):
        """Dodaj użytkownikowi element mapy"""

        profile = await Profile.get_for(member.id, member.guild.id)
        existing_segments = await self._get_existing_segments(profile)
        available_segments = self._get_available_segments(existing_segments)

        if element is None:
            element = random.choice(available_segments)

        if element not in available_segments:
            return await itx.response.send_message(
                f"Element #{element} jest już na mapie {member.mention}", ephemeral=True
            )

        await MapSegment.objects.create(profile=profile, number=element)
        await itx.response.send_message(
            f"Dodano element #{element} do mapy {member.mention}"
        )
        await self._check_map_completion(itx, profile)

    @app_commands.command(name="mapa-zabierz")  # type: ignore[arg-type]
    @app_commands.rename(member="użytkownik")
    @app_commands.describe(
        member="Użytkownik, któremu chcesz zabrać element mapy",
        element="Element mapy, który chcesz zabrać",
    )
    @app_commands.default_permissions(administrator=True)
    async def remove_map_element(self, itx: Interaction, member: Member, element: int):
        """Zabierz użytkownikowi konkretny element mapy"""

        profile = await Profile.get_for(member.id, member.guild.id)
        segment = await MapSegment.objects.filter(
            profile=profile, number=element
        ).get_or_none()

        if segment is None:
            return await itx.response.send_message(
                f"Element #{element} nie jest na mapie {member.mention}", ephemeral=True
            )

        await segment.delete()
        await itx.response.send_message(
            f"Zabrano element #{element} z mapy {member.mention}"
        )

    @app_commands.command(name="mapa-ranking")  # type: ignore[arg-type]
    async def completed_map_ranking(self, itx: Interaction):
        """Sprawdź kto ukończył mapę"""

        assert isinstance(itx.guild, Guild)
        completions = (
            await MapCompletion.objects.filter(profile__guild_id=itx.guild.id)
            .order_by("completed_at")
            .all()
        )

        def format_time(dt: datetime) -> str:
            timestamp = int(dt.timestamp())
            return f"<t:{timestamp}:R>"

        def page_formatter(items: list[MapCompletion], start_position: int) -> str:
            return "\n".join(
                f"{i}. <@{completion.profile.user_id}> - {format_time(completion.completed_at)}"
                for i, completion in enumerate(items, start_position)
            )

        view = Paginator(itx, "Ukończone mapy", completions, page_formatter)
        await itx.response.send_message(embed=view.get_embed(), view=view)

    @app_commands.command(name="mapa-ranking-czesci")  # type: ignore[arg-type]
    async def segment_ranking(self, itx: Interaction):
        """Sprawdź kto ma najwięcej części mapy"""

        assert isinstance(itx.guild, Guild)
        segments = (
            await MapSegment.objects.filter(profile__guild_id=itx.guild.id)
            .select_related("profile")
            .all()
        )
        segment_counts: Counter[int] = Counter(
            segment.profile.user_id for segment in segments
        )

        def page_formatter(items: list[tuple[int, int]], start_position: int) -> str:
            return "\n".join(
                f"{i}. <@{user_id}> - {count} części"
                for i, (user_id, count) in enumerate(items, start_position)
            )

        view = Paginator(
            itx, "Zebrane części mapy", segment_counts.most_common(), page_formatter
        )
        await itx.response.send_message(embed=view.get_embed(), view=view)

    async def _check_map_completion(self, itx: Interaction, profile: Profile):
        """Check if the user completed the map"""

        existing_segments = await self._get_existing_segments(profile)
        if len(existing_segments) == self.map_image_generator.SEGMENTS:
            await MapCompletion.objects.create(profile=profile)
            existing_completions = await MapCompletion.objects.filter(
                profile__guild_id=profile.guild_id
            ).count()

            embed = Embed(
                title="Ukończono mapę!",
                description=f"Gratulacje, ukończyłeś/aś mapę jako **{existing_completions}**!",
                color=EMBED_COLOR,
            )
            await itx.followup.send(embed=embed)

    async def _get_existing_segments(self, profile: Profile) -> list[int]:
        return await MapSegment.objects.filter(profile=profile).values_list(
            "number", flatten=True
        )

    def _get_available_segments(self, existing_segments: list[int]) -> list[int]:
        return [
            i
            for i in range(1, self.map_image_generator.SEGMENTS + 1)
            if i not in existing_segments
        ]
