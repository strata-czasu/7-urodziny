from typing import Awaitable, Callable

from discord import ButtonStyle, Interaction
from discord.ui import Button, View, button


class MapButtons(View):
    def __init__(
        self,
        buy_element_callback: Callable[[Interaction], Awaitable[None]] | None = None,
        *,
        timeout: float | None = None
    ) -> None:
        super().__init__(timeout=timeout)
        self._buy_element_callback = buy_element_callback

    @button(label="Kup element", style=ButtonStyle.green)
    async def on_buy_element(self, itx: Interaction, button: Button):
        if self._buy_element_callback is not None:
            return await self._buy_element_callback(itx)

        await itx.response.defer()
