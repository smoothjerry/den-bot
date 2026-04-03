from unittest.mock import MagicMock, AsyncMock, patch

# Patch aiosql.from_path before any test module imports points.repository,
# which calls aiosql.from_path at module level. The locally installed aiosql
# version may be incompatible with the project's SQL syntax, so we replace
# the call with a MagicMock to avoid parse errors during test collection.
_aiosql_patcher = patch("aiosql.from_path", return_value=MagicMock())
_aiosql_patcher.start()

import pytest


class AsyncIteratorMock:
    """Mock for Discord async iterators like thread.history()."""

    def __init__(self, items):
        self.items = iter(items)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            return next(self.items)
        except StopIteration:
            raise StopAsyncIteration


@pytest.fixture
def make_discord_message():
    """Factory fixture for creating mock Discord messages."""

    def _make(
        content="hello",
        author_bot=False,
        attachments=None,
        reference=None,
        channel=None,
        mentions=None,
    ):
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
def mock_db():
    """Fixture providing a mock Database and its mock connection."""
    db = MagicMock()
    mock_conn = MagicMock()
    db.connection.return_value.__enter__ = MagicMock(return_value=mock_conn)
    db.connection.return_value.__exit__ = MagicMock(return_value=False)
    return db, mock_conn
