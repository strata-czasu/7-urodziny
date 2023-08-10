from discord import Embed, Interaction

from birthday.constants import EMBED_COLOR
from birthday.models import MapCompletion, MapSegment, Profile

from .map_image import MapImageGenerator


async def check_map_completion(itx: Interaction, profile: Profile):
    """Check if the user completed the map"""

    existing_segments = await get_existing_segments(profile)
    if len(existing_segments) == MapImageGenerator.SEGMENTS:
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


async def get_existing_segments(profile: Profile) -> list[int]:
    return await MapSegment.objects.filter(profile=profile).values_list(
        "number", flatten=True
    )


def get_available_segments(existing_segments: list[int]) -> list[int]:
    return [
        i
        for i in range(1, MapImageGenerator.SEGMENTS + 1)
        if i not in existing_segments
    ]
