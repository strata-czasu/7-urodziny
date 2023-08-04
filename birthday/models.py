from __future__ import annotations

import databases
import ormar
import sqlalchemy

from birthday.utils import get_database_url

database = databases.Database(get_database_url())
metadata = sqlalchemy.MetaData()


class BaseMeta(ormar.ModelMeta):
    database = database
    metadata = metadata


class Profile(ormar.Model):
    id: int = ormar.Integer(primary_key=True)
    user_id: int = ormar.BigInteger()
    guild_id: int = ormar.BigInteger()
    points: int = ormar.Integer()

    class Meta(BaseMeta):
        tablename = "profile"

    @classmethod
    async def get_for(cls, user_id: int, guild_id: int) -> Profile:
        defaults = {"points": 0}
        profile, _ = await cls.objects.get_or_create(
            defaults, user_id=user_id, guild_id=guild_id
        )
        return profile


class MapSegment(ormar.Model):
    id: int = ormar.Integer(primary_key=True)
    profile: Profile = ormar.ForeignKey(Profile, nullable=False)
    number = ormar.Integer(minimum=1, maximum=30)

    class Meta(BaseMeta):
        tablename = "map_segment"
        constraints = [ormar.UniqueColumns("profile", "number")]
