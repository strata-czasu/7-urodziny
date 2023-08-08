from typing import Awaitable, Callable, Generic, TypeVar

from discord import Embed, Interaction, Member, User
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


class UserSelectView(View):
    def __init__(
        self,
        target: Interaction,
        callback: Callable[[Interaction, list[Member | User]], Awaitable[None]],
        *,
        timeout: float | None = 180,
    ) -> None:
        super().__init__(timeout=timeout)
        self._target = target
        self._callback = callback

    @select(
        cls=UserSelect,
        placeholder="Wybierz użytkowników",
        min_values=1,
        max_values=25,
    )
    async def user_select(self, itx: Interaction, select: UserSelect):
        await self._callback(itx, select.values)
        await self.on_timeout()
        self.stop()

    async def on_timeout(self) -> None:
        self.clear_items()
        await self._target.edit_original_response(view=None)
