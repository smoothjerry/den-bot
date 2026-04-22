from unittest.mock import AsyncMock, MagicMock

import discord

from denbot.discord.messages import (
    CHAIN_LIMIT,
    fetch_reply_chain,
    format_message_coversation,
    get_thread_history,
    map_reply_chain_to_api_format,
)
from tests.conftest import AsyncIteratorMock


def _make_msg(content, bot=False):
    msg = MagicMock()
    msg.content = content
    msg.author.bot = bot
    return msg


class TestMapReplyChainToApiFormat:
    def test_empty_chain(self):
        assert map_reply_chain_to_api_format([]) == []

    def test_user_message_role(self):
        result = map_reply_chain_to_api_format([_make_msg("hi", bot=False)])
        assert result[0]["role"] == "user"

    def test_bot_message_role(self):
        result = map_reply_chain_to_api_format([_make_msg("hello", bot=True)])
        assert result[0]["role"] == "assistant"

    def test_mixed_chain_preserves_order(self):
        msgs = [
            _make_msg("a", bot=False),
            _make_msg("b", bot=True),
            _make_msg("c", bot=False),
            _make_msg("d", bot=True),
        ]
        result = map_reply_chain_to_api_format(msgs)
        assert [m["role"] for m in result] == ["user", "assistant", "user", "assistant"]
        assert [m["content"] for m in result] == ["a", "b", "c", "d"]

    def test_content_preserved(self):
        result = map_reply_chain_to_api_format([_make_msg("exact content here")])
        assert result[0]["content"] == "exact content here"


class TestGetThreadHistory:
    async def test_returns_messages(self):
        msgs = [_make_msg("a"), _make_msg("b"), _make_msg("c")]
        thread = MagicMock(spec=discord.Thread)
        thread.history.return_value = AsyncIteratorMock(msgs)
        result = await get_thread_history(thread)
        assert result == msgs

    async def test_passes_chain_limit(self):
        thread = MagicMock(spec=discord.Thread)
        thread.history.return_value = AsyncIteratorMock([])
        await get_thread_history(thread)
        thread.history.assert_called_once_with(limit=CHAIN_LIMIT)


class TestFetchReplyChain:
    async def test_no_reference(self):
        msg = MagicMock()
        msg.channel = MagicMock(spec=discord.TextChannel)
        msg.reference = None
        chain, is_thread, count = await fetch_reply_chain(msg)
        assert chain == []
        assert is_thread is False
        assert count == 0

    async def test_single_reply(self):
        parent = _make_msg("parent")
        parent.reference = None

        msg = MagicMock()
        msg.channel = MagicMock(spec=discord.TextChannel)
        msg.reference = MagicMock()
        msg.reference.message_id = 111
        msg.channel.fetch_message = AsyncMock(return_value=parent)

        chain, is_thread, count = await fetch_reply_chain(msg)
        assert len(chain) == 1
        assert chain[0] is parent
        assert is_thread is False
        assert count == 1

    async def test_deep_chain_reversed(self):
        """A 3-deep reply chain should be returned oldest-first."""
        channel = MagicMock(spec=discord.TextChannel)

        msg_a = _make_msg("oldest")
        msg_a.reference = None
        msg_a.channel = channel

        msg_b = _make_msg("middle")
        msg_b.reference = MagicMock()
        msg_b.reference.message_id = 100
        msg_b.channel = channel

        msg_c = _make_msg("newest parent")
        msg_c.reference = MagicMock()
        msg_c.reference.message_id = 101
        msg_c.channel = channel

        # First fetch returns msg_c (the direct parent), then msg_b, then msg_a
        channel.fetch_message = AsyncMock(side_effect=[msg_c, msg_b, msg_a])

        trigger = MagicMock()
        trigger.channel = channel
        trigger.reference = MagicMock()
        trigger.reference.message_id = 102

        chain, is_thread, count = await fetch_reply_chain(trigger)
        assert [m.content for m in chain] == ["oldest", "middle", "newest parent"]
        assert is_thread is False
        assert count == 3

    async def test_chain_limit_respected(self):
        """Chain should stop at CHAIN_LIMIT even if more replies exist."""
        channel = MagicMock(spec=discord.TextChannel)

        # Build a chain longer than CHAIN_LIMIT
        messages = []
        for i in range(CHAIN_LIMIT + 5):
            m = _make_msg(f"msg-{i}")
            m.reference = MagicMock()
            m.reference.message_id = 1000 + i
            m.channel = channel
            messages.append(m)
        # Last message in chain has no reference
        messages[-1].reference = None

        channel.fetch_message = AsyncMock(side_effect=messages)

        trigger = MagicMock()
        trigger.channel = channel
        trigger.reference = MagicMock()
        trigger.reference.message_id = 999

        chain, is_thread, count = await fetch_reply_chain(trigger)
        assert len(chain) == CHAIN_LIMIT
        assert count == CHAIN_LIMIT

    async def test_thread_delegates_to_history(self):
        thread_msgs = [_make_msg("t1"), _make_msg("t2")]
        thread = MagicMock(spec=discord.Thread)
        thread.history.return_value = AsyncIteratorMock(thread_msgs)

        msg = MagicMock()
        msg.channel = thread

        chain, is_thread, count = await fetch_reply_chain(msg)
        assert chain == thread_msgs
        assert is_thread is True
        assert count == -1


class TestFormatMessageCoversation:
    async def test_formats_reply_chain(self):
        """Integration test: real internal calls, mocked Discord I/O."""
        parent = _make_msg("parent question", bot=False)
        parent.reference = None

        msg = MagicMock()
        msg.channel = MagicMock(spec=discord.TextChannel)
        msg.reference = MagicMock()
        msg.reference.message_id = 111
        msg.channel.fetch_message = AsyncMock(return_value=parent)

        formatted, is_thread, count = await format_message_coversation(msg)
        assert len(formatted) == 1
        assert formatted[0] == {"role": "user", "content": "parent question"}
        assert is_thread is False
        assert count == 1

    async def test_thread_conversation(self):
        thread_msgs = [
            _make_msg("user msg", bot=False),
            _make_msg("bot reply", bot=True),
        ]
        thread = MagicMock(spec=discord.Thread)
        thread.history.return_value = AsyncIteratorMock(thread_msgs)

        msg = MagicMock()
        msg.channel = thread

        formatted, is_thread, count = await format_message_coversation(msg)
        assert len(formatted) == 2
        assert formatted[0]["role"] == "user"
        assert formatted[1]["role"] == "assistant"
        assert is_thread is True
