import asyncio
import logging
from datetime import datetime

from discord.ext import commands
from discord.ext.commands import CommandError, errors
from discord.ext.commands.context import Context

from birthday.models import database

from .config import Config

log = logging.getLogger(__name__)


class Bot(commands.Bot):
    def __init__(self, config: Config | None = None) -> None:
        self._config = config or Config.default()
        log.info("Initializing bot")

        super().__init__(
            command_prefix=commands.when_mentioned,
            intents=self._config._intents,
            allowed_mentions=self._config._allowed_mentions,
            help_command=None,
        )

        self.start_timestamp = datetime.utcnow()

    async def setup_hook(self) -> None:
        await database.connect()
        await self.load_extensions()

    async def close(self) -> None:
        await super().close()
        await database.disconnect()

    async def load_extension(self, name: str, *, package: str | None = None) -> None:
        if package is None:
            package = self._config._extension_package

        return await super().load_extension(name, package=package)

    async def reload_extension(self, name: str, *, package: str | None = None) -> None:
        if package is None:
            package = self._config._extension_package

        return await super().reload_extension(name, package=package)

    async def load_extensions(self) -> None:
        if len(self._config._extensions) == 0:
            return

        await asyncio.gather(
            *[self.load_extension(ext) for ext in self._config._extensions]
        )

        log.info(
            "Loaded %d extension(s): %s",
            len(self.extensions),
            ", ".join(self.extensions.keys()),
        )

    async def reload_extensions(self) -> None:
        if len(self._config._extensions) == 0:
            return

        await asyncio.gather(
            *[self.reload_extension(ext) for ext in self._config._extensions]
        )

        log.info("Reloaded %d extension(s)", len(self.extensions))

    async def on_command_error(self, context: Context, exception: CommandError) -> None:
        if isinstance(exception, errors.CommandNotFound):
            return
        if isinstance(exception, errors.CheckFailure):
            await context.send(str(exception))
            return

        await super().on_command_error(context, exception)
