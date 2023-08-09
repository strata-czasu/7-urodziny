from typing import Awaitable, Callable, Generic, TypeVar

from discord import ButtonStyle, Embed, Interaction, Member, User
from discord.ui import Button, UserSelect, View, button, select

from birthday.constants import EMBED_COLOR

__all__ = ("Paginator", "UserSelectView")

T = TypeVar("T")


class Paginator(Generic[T], View):
    def __init__(
        self,
        target: Interaction,
        title: str,
        elements: list[T],
        formatter: Callable[[list[T], int], str],
        *,
        per_page: int = 10,
        timeout: float | None = 180,
    ) -> None:
        super().__init__(timeout=timeout)
        self._target = target
        self._title = title
        self._elements = elements
        self._elements_per_page = per_page
        self._current_page = 0
        self._page_formatter = formatter

    @property
    def total_pages(self) -> int:
        return (len(self._elements) - 1) // self._elements_per_page + 1

    @property
    def page_start(self) -> int:
        return self._current_page * self._elements_per_page

    @property
    def page_end(self) -> int:
        return self.page_start + self._elements_per_page

    def get_embed(self) -> Embed:
        page = self._get_page()
        description = self._page_formatter(page, self.page_start + 1)
        footer = f"{self._current_page + 1}/{self.total_pages}"

        embed = Embed(title=self._title, description=description, color=EMBED_COLOR)
        embed.set_footer(text=footer)
        return embed

    def _get_page(self) -> list[T]:
        start = self.page_start
        end = self.page_end
        return self._elements[start:end]

    def _switch_page(self, count: int) -> None:
        self._current_page = (self._current_page + count) % self.total_pages

    @button(emoji="⬅️")
    async def on_left_arrow(self, itx: Interaction, button: Button):
        self._switch_page(-1)
        await itx.response.edit_message(embed=self.get_embed())

    @button(emoji="➡️")
    async def on_right_arrow(self, itx: Interaction, button: Button):
        self._switch_page(1)
        await itx.response.edit_message(embed=self.get_embed())

    async def on_timeout(self) -> None:
        self.clear_items()
        await self._target.edit_original_response(view=None)


UserSelectCallback = Callable[[Interaction, list[Member | User]], Awaitable[None]]


class UserSelectView(View):
    MIN_VALUES = 1
    MAX_VALUES = 25

    def __init__(
        self,
        target: Interaction,
        accept_callback: UserSelectCallback,
        change_callback: UserSelectCallback | None = None,
        cancel_callback: Callable[[Interaction], Awaitable[None]] | None = None,
        *,
        timeout: float | None = 180,
    ) -> None:
        super().__init__(timeout=timeout)
        self._target = target
        self._change_callback = change_callback
        self._accept_callback = accept_callback
        self._cancel_callback = cancel_callback
        self._selected_values: list[Member | User] = []

    @select(
        cls=UserSelect,
        placeholder="Wybierz użytkowników",
        min_values=MIN_VALUES,
        max_values=MAX_VALUES,
    )
    async def user_select(self, itx: Interaction, select: UserSelect):
        self._selected_values = select.values
        if self._change_callback is not None:
            return await self._change_callback(itx, select.values)

        await itx.response.defer()

    @button(label="Wyślij", style=ButtonStyle.green)
    async def on_send(self, itx: Interaction, button: Button):
        await self._accept_callback(itx, self._selected_values)

        await self.cleanup()
        self.stop()

    @button(label="Anuluj", style=ButtonStyle.red)
    async def on_cancel(self, itx: Interaction, button: Button):
        if self._cancel_callback is not None:
            return await self._cancel_callback(itx)

        await self.cleanup()
        self.stop()

    async def on_timeout(self) -> None:
        await self.cleanup()

    async def cleanup(self) -> None:
        self.clear_items()
        await self._target.edit_original_response(view=None)
