import logging
from os import environ

from discord import AllowedMentions, Intents

from birthday.common import Bot, Config


def main() -> None:
    config = (
        Config.default()
        .allowed_mentions(AllowedMentions.none())
        .extension_package("birthday.extensions")
        .extension(".management")
        .extension(".info")
    )
    bot = Bot(config)

    # Token is stored outside of the config object for security reasons
    token = environ.get("BOT_TOKEN")
    if token is None:
        raise ValueError("BOT_TOKEN environment variable is not set")
    bot.run(token, log_handler=None)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    main()
