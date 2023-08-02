from os import environ

from discord import Asset, Member, User


def get_env(key: str, default: str | None = None) -> str:
    """Get an environment variable, or raise an error if no default is provided"""

    value = environ.get(key)
    if value is None:
        if default is None:
            raise ValueError(f"{key} environment variable is not set")
        return default
    return value


def get_database_url() -> str:
    """Get a Postgres database url from environment variables"""

    host = get_env("POSTGRES_HOST", "localhost")
    port = get_env("POSTGRES_PORT", "5432")
    user = get_env("POSTGRES_USER")
    password = get_env("POSTGRES_PASSWORD")
    database = get_env("POSTGRES_DB")

    return f"postgresql://{user}:{password}@{host}:{port}/{database}"


def format_bool(
    value: bool,
    *,
    positive: str = "Yes",
    negative: str = "No",
) -> str:
    return positive if value else negative


def get_user_avatar(user: User | Member) -> Asset:
    """
    Returns user avatar Asset

    - If user is a `Member` and has a guild avatar, return `guild_avatar`
    - If user has a normal avatar, return `avatar`
    - If user doesn't have a guild avatar, nor a normal avatar, return `default_avatar`

    - If user has an animated avatar, return it with the 'gif' format
    """

    avatar = user.display_avatar

    if avatar.is_animated():
        avatar = avatar.with_format("gif")

    return avatar
