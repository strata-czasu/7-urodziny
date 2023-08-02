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
