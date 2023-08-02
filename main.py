import logging

from discord import AllowedMentions, Intents

from birthday.common import Bot, Config
from birthday.utils import get_env


def main() -> None:
    config = (
        Config.default()
        .allowed_mentions(AllowedMentions.none())
        .extension_package("birthday.extensions")
        .extension(".management")
        .extension(".info")
        .extension(".users")
    )
    bot = Bot(config)

    # Token is stored outside of the config object for security reasons
    token = get_env("BOT_TOKEN")
    bot.run(token, log_handler=None)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    main()
