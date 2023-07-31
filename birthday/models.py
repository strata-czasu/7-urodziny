from os import environ

import databases
import ormar
import sqlalchemy

DATABASE_URL = environ.get("DB_URL", "")

database = databases.Database(DATABASE_URL)
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
