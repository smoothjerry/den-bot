from unittest.mock import patch, AsyncMock, MagicMock

import pytest

from denbot.ai.claude import ClaudeHandler
from denbot.ai.config import DENJAMIN_SYSTEM_PROMPT


@pytest.fixture
def handler():
    with patch("denbot.ai.claude.AsyncAnthropic"):
        h = ClaudeHandler(api_key="fake-key")
    # Replace the client.messages.create with an AsyncMock after construction
    mock_response = MagicMock()
    mock_response.content = [MagicMock(text="bot reply")]
    h.client.messages.create = AsyncMock(return_value=mock_response)
    return h


class TestCoalesceMessages:
    def test_empty_list(self, handler):
        assert handler._coalesce_messages([]) == []

    def test_single_message(self, handler):
        msgs = [{"role": "user", "content": "hi"}]
        result = handler._coalesce_messages(msgs)
        assert result == [{"role": "user", "content": "hi"}]

    def test_alternating_roles_no_merge(self, handler):
        msgs = [
            {"role": "user", "content": "a"},
            {"role": "assistant", "content": "b"},
            {"role": "user", "content": "c"},
        ]
        result = handler._coalesce_messages(msgs)
        assert len(result) == 3
        assert result[0]["content"] == "a"
        assert result[1]["content"] == "b"
        assert result[2]["content"] == "c"

    def test_consecutive_same_role_merged(self, handler):
        msgs = [
            {"role": "user", "content": "a"},
            {"role": "user", "content": "b"},
        ]
        result = handler._coalesce_messages(msgs)
        assert len(result) == 1
        assert result[0]["content"] == "a\nb"

    def test_three_consecutive_merged(self, handler):
        msgs = [
            {"role": "user", "content": "a"},
            {"role": "user", "content": "b"},
            {"role": "user", "content": "c"},
        ]
        result = handler._coalesce_messages(msgs)
        assert len(result) == 1
        assert result[0]["content"] == "a\nb\nc"

    def test_mixed_merge_and_keep(self, handler):
        msgs = [
            {"role": "user", "content": "a"},
            {"role": "user", "content": "b"},
            {"role": "assistant", "content": "c"},
            {"role": "user", "content": "d"},
        ]
        result = handler._coalesce_messages(msgs)
        assert len(result) == 3
        assert result[0] == {"role": "user", "content": "a\nb"}
        assert result[1] == {"role": "assistant", "content": "c"}
        assert result[2] == {"role": "user", "content": "d"}

    def test_does_not_mutate_input(self, handler):
        msgs = [
            {"role": "user", "content": "a"},
            {"role": "user", "content": "b"},
        ]
        original_first = msgs[0].copy()
        original_second = msgs[1].copy()
        handler._coalesce_messages(msgs)
        assert msgs[0] == original_first
        assert msgs[1] == original_second

    def test_non_string_content_not_merged(self, handler):
        """When consecutive same-role messages can't be string-merged (e.g. one has
        image blocks), both messages are preserved rather than silently dropped."""
        image_block = [{"type": "image", "source": {"type": "url", "url": "http://example.com/img.png"}}]
        msgs = [
            {"role": "user", "content": image_block},
            {"role": "user", "content": "describe it"},
        ]
        result = handler._coalesce_messages(msgs)
        assert len(result) == 2
        assert result[0]["content"] is image_block
        assert result[1]["content"] == "describe it"


class TestGenerateResponse:
    async def test_basic_response(self, handler):
        result = await handler.generate_response("hi", None, [])
        assert result == "bot reply"
        handler.client.messages.create.assert_called_once()
        call_kwargs = handler.client.messages.create.call_args.kwargs
        assert call_kwargs["messages"] == [{"role": "user", "content": "hi"}]
        assert call_kwargs["system"] == DENJAMIN_SYSTEM_PROMPT

    async def test_with_conversation_context(self, handler):
        context = [
            {"role": "user", "content": "earlier"},
            {"role": "assistant", "content": "response"},
        ]
        await handler.generate_response("follow up", context, [])
        call_kwargs = handler.client.messages.create.call_args.kwargs
        messages = call_kwargs["messages"]
        assert len(messages) == 3
        assert messages[0]["content"] == "earlier"
        assert messages[1]["content"] == "response"
        assert messages[2]["content"] == "follow up"

    async def test_with_image_data(self, handler):
        image_data = [{"type": "image", "source": {"type": "url", "url": "http://example.com/img.png"}}]
        await handler.generate_response("describe this", None, image_data)
        call_kwargs = handler.client.messages.create.call_args.kwargs
        messages = call_kwargs["messages"]
        content = messages[0]["content"]
        assert isinstance(content, list)
        assert content[0] == {"type": "text", "text": "describe this"}
        assert content[1] == image_data[0]

    async def test_with_context_and_images(self, handler):
        context = [{"role": "assistant", "content": "hi there"}]
        image_data = [{"type": "image", "source": {"type": "url", "url": "http://example.com/img.png"}}]
        await handler.generate_response("look at this", context, image_data)
        call_kwargs = handler.client.messages.create.call_args.kwargs
        messages = call_kwargs["messages"]
        assert len(messages) == 2
        assert messages[0]["content"] == "hi there"
        assert isinstance(messages[1]["content"], list)

    async def test_api_error_returns_error_string(self, handler):
        handler.client.messages.create = AsyncMock(side_effect=Exception("API down"))
        result = await handler.generate_response("hi", None, [])
        assert result == "Error: API down"

    async def test_coalescing_applied(self, handler):
        context = [{"role": "user", "content": "first message"}]
        await handler.generate_response("second message", context, [])
        call_kwargs = handler.client.messages.create.call_args.kwargs
        messages = call_kwargs["messages"]
        # Two consecutive user messages should be coalesced into one
        assert len(messages) == 1
        assert messages[0]["content"] == "first message\nsecond message"

    async def test_default_model(self, handler):
        await handler.generate_response("hi", None, [])
        call_kwargs = handler.client.messages.create.call_args.kwargs
        assert call_kwargs["model"] == "claude-sonnet-4-20250514"
