from collections.abc import Callable
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest


class AsyncIteratorMock:
    """Mock for Discord async iterators like thread.history()."""

    def __init__(self, items: list[Any]) -> None:
        self.items = iter(items)

    def __aiter__(self) -> "AsyncIteratorMock":
        return self

    async def __anext__(self) -> Any:
        try:
            return next(self.items)
        except StopIteration:
            raise StopAsyncIteration


@pytest.fixture
def make_discord_message() -> Callable[..., MagicMock]:
    """Factory fixture for creating mock Discord messages."""

    def _make(
        content: str = "hello",
        author_bot: bool = False,
        attachments: list[Any] | None = None,
        reference: Any = None,
        channel: Any = None,
        mentions: list[Any] | None = None,
    ) -> MagicMock:
        msg = MagicMock()
        msg.content = content
        msg.author.bot = author_bot
        msg.author.display_name = "TestUser"
        msg.author.id = 99999
        msg.attachments = attachments or []
        msg.reference = reference
        msg.channel = channel or MagicMock()
        msg.channel.fetch_message = AsyncMock()
        msg.channel.send = AsyncMock()
        msg.reply = AsyncMock()
        msg.create_thread = AsyncMock()
        msg.mentions = mentions or []
        return msg

    return _make


@pytest.fixture
def mock_db() -> tuple[MagicMock, MagicMock]:
    """Fixture providing a mock Database and its mock connection."""
    db = MagicMock()
    mock_conn = MagicMock()
    db.connection.return_value.__enter__ = MagicMock(return_value=mock_conn)
    db.connection.return_value.__exit__ = MagicMock(return_value=False)
    return db, mock_conn
