from unittest.mock import patch

import pytest

from ai.claude import ClaudeHandler


@pytest.fixture
def handler():
    with patch("ai.claude.AsyncAnthropic"):
        return ClaudeHandler(api_key="fake-key")


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
        """When both consecutive same-role messages have string content, they merge.
        When either has non-string content (e.g. image blocks), the isinstance check
        prevents merging — but the current implementation also drops the second message
        since it's neither merged nor appended. This test documents that behavior."""
        image_block = [{"type": "image", "source": {"type": "url", "url": "http://example.com/img.png"}}]
        msgs = [
            {"role": "user", "content": image_block},
            {"role": "user", "content": "describe it"},
        ]
        result = handler._coalesce_messages(msgs)
        # Second message is dropped because same-role branch doesn't append on isinstance failure
        assert len(result) == 1
        assert result[0]["content"] is image_block
