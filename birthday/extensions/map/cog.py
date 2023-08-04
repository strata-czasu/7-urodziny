import random
from io import BytesIO

from discord import Color, Embed, File, Interaction, Member, app_commands

from birthday.common import Cog
from birthday.common.bot import Bot
from birthday.models import MapSegment, Profile

from .map_image import MapImageGenerator


@app_commands.guild_only()
class Map(Cog):
    MAP_ELEMENT_COST = 150

    def __init__(self, bot: Bot) -> None:
        super().__init__(bot)
        self.map_image_generator = MapImageGenerator()

    @app_commands.command(name="mapa")  # type: ignore[arg-type]
    async def show_map(self, itx: Interaction, member: Member | None = None):
        """Sprawdź aktualny postęp na mapie"""

        if member is None:
            assert isinstance(itx.user, Member)
            member = itx.user

        await itx.response.defer()

        profile = await Profile.get_for(member.id, member.guild.id)
        segments: list[int] = await MapSegment.objects.filter(
            profile=profile
        ).values_list("number", flatten=True)

        filename = "mapa.png"
        with BytesIO() as image_binary:
            map_image = self.map_image_generator.get_image(segments)
            # TODO: Compress image to save transfer and speed up uploading
            map_image.save(image_binary, format="png")
            image_binary.seek(0)
            file = File(image_binary, filename)

        embed = Embed(
            title=f"Mapa {member.display_name}",
            description=f"Masz już **{len(segments)}/{self.map_image_generator.SEGMENTS}** części mapy!",
            color=Color.from_str("#f9b800"),
        )
        embed.set_image(url=f"attachment://{filename}")
        await itx.followup.send(embed=embed, file=file)

    @app_commands.command(name="mapa-kup")  # type: ignore[arg-type]
    async def buy_map_element(self, itx: Interaction):
        """Kup losową część mapy"""

        assert isinstance(itx.user, Member)
        profile = await Profile.get_for(itx.user.id, itx.user.guild.id)
        if profile.points < self.MAP_ELEMENT_COST:
            return await itx.response.send_message(
                f"Nie masz wystarczająco punktów, potrzebujesz {self.MAP_ELEMENT_COST} pkt",
                ephemeral=True,
            )

        existing_segments: list[int] = await MapSegment.objects.filter(
            profile=profile
        ).values_list("number", flatten=True)
        available_segments = self._get_available_segments(existing_segments)
        if len(available_segments) == 0:
            return await itx.response.send_message(
                f"Masz już wszystkie części mapy!", ephemeral=True
            )

        segment = random.choice(available_segments)
        await MapSegment.objects.create(profile=profile, number=segment)
        profile.points -= self.MAP_ELEMENT_COST
        await profile.update()
        await itx.response.send_message(
            f"Kupiłeś/aś część mapy #{segment} za {self.MAP_ELEMENT_COST} pkt"
        )

    @app_commands.command(name="mapa-dodaj")  # type: ignore[arg-type]
    @app_commands.describe(
        element="Element mapy, który chcesz dodać (domyślnie losowy)"
    )
    @app_commands.default_permissions(administrator=True)
    async def add_map_element(
        self, itx: Interaction, member: Member, element: int | None
    ):
        """Dodaj użytkownikowi element mapy"""

        profile = await Profile.get_for(member.id, member.guild.id)
        existing_segments: list[int] = await MapSegment.objects.filter(
            profile=profile
        ).values_list("number", flatten=True)
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

    @app_commands.command(name="mapa-zabierz")  # type: ignore[arg-type]
    @app_commands.describe(element="Element mapy, który chcesz zabrać")
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

    def _get_available_segments(self, existing_segments: list[int]) -> list[int]:
        return [
            i
            for i in range(1, self.map_image_generator.SEGMENTS + 1)
            if i not in existing_segments
        ]
