from unittest.mock import MagicMock

from discord_utils.messages import map_reply_chain_to_api_format


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
