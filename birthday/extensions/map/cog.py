from io import BytesIO

from discord import Color, Embed, File, Interaction, Member, app_commands

from birthday.common import Cog
from birthday.common.bot import Bot

from .map_image import MapImageGenerator


@app_commands.guild_only()
class Map(Cog):
    def __init__(self, bot: Bot) -> None:
        super().__init__(bot)
        self.map_image_generator = MapImageGenerator()

    @app_commands.command(name="mapa")  # type: ignore[arg-type]
    async def show_map(self, itx: Interaction, member: Member | None = None):
        if member is None:
            assert isinstance(itx.user, Member)
            member = itx.user

        await itx.response.defer()
        # TODO: Get User's segments from database
        segments = list(range(1, 31))
        filename = "mapa.png"
        with BytesIO() as image_binary:
            map_image = self.map_image_generator.get_image(segments)
            # TODO: Compress image to save transfer and speed up uploading
            map_image.save(image_binary, format="png")
            image_binary.seek(0)
            file = File(image_binary, filename)

        embed = Embed(
            title=f"Mapa {member.display_name}",
            description=f"Masz już **{len(segments)}/{self.map_image_generator.SEGMENTS}** elementów mapy",
            color=Color.from_str("#f9b800"),
        )
        embed.set_image(url=f"attachment://{filename}")
        await itx.followup.send(embed=embed, file=file)
