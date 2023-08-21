from __future__ import annotations

from io import BytesIO
from random import choice

from discord import ButtonStyle, Embed, File, Interaction
from discord.ui import Button, View, button

from birthday.constants import EMBED_COLOR, MAP_ELEMENT_COST
from birthday.extensions.map.map_image import MapImageGenerator
from birthday.extensions.map.utils import get_available_segments
from birthday.models import MapSegment, Profile


class MapImageView(View):
    FILENAME = "mapa.jpg"

    def __init__(
        self,
        target: Interaction,
        title: str,
        profile: Profile,
        segments: list[int],
        image_generator: MapImageGenerator,
        *,
        timeout: float | None = None,
    ) -> None:
        super().__init__(timeout=timeout)
        self._target = target
        self._title = title
        self._profile = profile
        self._segments = segments
        self._available_segments = get_available_segments(segments)
        self._image_generator = image_generator

    def get_embed(self) -> Embed:
        description = self.get_description()
        embed = Embed(title=self._title, description=description, color=EMBED_COLOR)
        embed.set_image(url=f"attachment://{self.FILENAME}")

        return embed

    def get_description(self) -> str:
        description = (
            f"Masz już **{len(self._segments)}/{MapImageGenerator.SEGMENTS}** "
            f"części mapy!"
        )
        if len(self._segments) == MapImageGenerator.SEGMENTS:
            description += " Gratulacje!"

        return description

    def get_map_image(self) -> File:
        with BytesIO() as image_binary:
            map_image = self._image_generator.get_image(self._segments)
            map_image.save(image_binary, format="jpeg", optimize=True, quality=85)
            image_binary.seek(0)
            file = File(image_binary, self.FILENAME)

        return file

    def can_buy_element(self) -> bool:
        return (
            self._profile.points >= MAP_ELEMENT_COST
            and len(self.available_segments) > 0
        )

    @property
    def available_segments(self) -> list[int]:
        return self._available_segments

    @button(label="Kup element", style=ButtonStyle.green)
    async def on_buy_element(self, itx: Interaction, button: Button):
        if self._target.user.id != itx.user.id:
            return await itx.response.send_message(
                "Nie możesz kupić elementu mapy, bo nie jesteś jej właścicielem!",
                ephemeral=True,
            )

        if not self.can_buy_element():
            return await itx.response.send_message(
                f"Nie masz wystarczająco dukatów, potrzebujesz **{MAP_ELEMENT_COST}** 🪙",
                ephemeral=True,
            )

        segment = choice(self._available_segments)
        self._segments.append(segment)
        self._available_segments.remove(segment)

        await MapSegment.objects.create(profile=self._profile, number=segment)
        self._profile.points -= MAP_ELEMENT_COST
        await self._profile.update()

        embed = Embed(
            title="Zakupiono część mapy!",
            description=f"Masz aktualnie **{len(self._segments)}/"
            f"{self._image_generator.SEGMENTS}** części mapy!",
            color=EMBED_COLOR,
        )
        await itx.response.send_message(embed=embed, ephemeral=True)

        new_map_file = self.get_map_image()
        await self._target.edit_original_response(
            embed=self.get_embed(), attachments=[new_map_file]
        )

        if not self.can_buy_element():
            button.disabled = True
            await self._target.edit_original_response(view=self)

    async def on_timeout(self) -> None:
        self.clear_items()
        await self._target.edit_original_response(view=None)
