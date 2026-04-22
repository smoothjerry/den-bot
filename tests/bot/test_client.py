from unittest.mock import AsyncMock, MagicMock, patch

import discord
import pytest

from denbot.bot.client import REPLY_LIMIT, MyBot, create_bot


@pytest.fixture
def bot_and_mocks():
    mock_chatbot = AsyncMock()
    mock_chatbot.generate_response = AsyncMock(return_value="bot reply")
    mock_points_repo = MagicMock()
    mock_db = MagicMock()

    with patch("denbot.bot.client.register_points_commands"):
        bot = MyBot(mock_chatbot, mock_points_repo, mock_db)

    # discord.Client.user is a read-only property, so we patch it on the class
    mock_user = MagicMock()
    mock_user.id = 12345
    with patch.object(
        type(bot), "user", new_callable=lambda: property(lambda self: mock_user)
    ):
        yield bot, mock_chatbot, mock_db


class TestOnMessage:
    async def test_ignores_own_messages(self, bot_and_mocks):
        bot, mock_chatbot, mock_db = bot_and_mocks
        message = MagicMock()
        message.author = bot.user

        await bot.on_message(message)

        mock_chatbot.generate_response.assert_not_called()

    async def test_ignores_no_mention(self, bot_and_mocks):
        bot, mock_chatbot, mock_db = bot_and_mocks
        message = MagicMock()
        message.author = MagicMock()
        message.mentions = []

        await bot.on_message(message)

        mock_chatbot.generate_response.assert_not_called()

    @patch("denbot.bot.client.format_message_coversation", new_callable=AsyncMock)
    @patch("denbot.bot.client.format_attachment_data")
    async def test_replies_in_thread(
        self, mock_attachments, mock_conversation, bot_and_mocks
    ):
        bot, mock_chatbot, mock_db = bot_and_mocks
        mock_attachments.return_value = []
        mock_conversation.return_value = ([], True, -1)

        message = MagicMock()
        message.author = MagicMock()
        message.mentions = [bot.user]
        message.content = f"<@{bot.user.id}> hello"
        message.channel.send = AsyncMock()

        await bot.on_message(message)

        message.channel.send.assert_called_once_with("bot reply")
        message.reply.assert_not_called()

    @patch("denbot.bot.client.format_message_coversation", new_callable=AsyncMock)
    @patch("denbot.bot.client.format_attachment_data")
    async def test_replies_normally_under_limit(
        self, mock_attachments, mock_conversation, bot_and_mocks
    ):
        bot, mock_chatbot, mock_db = bot_and_mocks
        mock_attachments.return_value = []
        mock_conversation.return_value = ([], False, 3)

        message = MagicMock()
        message.author = MagicMock()
        message.mentions = [bot.user]
        message.content = f"<@{bot.user.id}> hello"
        message.reply = AsyncMock()

        await bot.on_message(message)

        message.reply.assert_called_once_with("bot reply")

    @patch("denbot.bot.client.format_message_coversation", new_callable=AsyncMock)
    @patch("denbot.bot.client.format_attachment_data")
    async def test_creates_thread_over_limit(
        self, mock_attachments, mock_conversation, bot_and_mocks
    ):
        bot, mock_chatbot, mock_db = bot_and_mocks
        mock_attachments.return_value = []
        mock_conversation.return_value = ([], False, REPLY_LIMIT + 1)

        mock_thread = MagicMock()
        mock_thread.send = AsyncMock()

        message = MagicMock()
        message.author = MagicMock()
        message.author.display_name = "TestUser"
        message.mentions = [bot.user]
        message.content = f"<@{bot.user.id}> hello"
        message.create_thread = AsyncMock(return_value=mock_thread)

        await bot.on_message(message)

        message.create_thread.assert_called_once_with(name="Conversation with TestUser")
        mock_thread.send.assert_called_once_with("bot reply")
        message.reply.assert_not_called()

    @patch("denbot.bot.client.format_message_coversation", new_callable=AsyncMock)
    @patch("denbot.bot.client.format_attachment_data")
    async def test_strips_mention_from_input(
        self, mock_attachments, mock_conversation, bot_and_mocks
    ):
        bot, mock_chatbot, mock_db = bot_and_mocks
        mock_attachments.return_value = []
        mock_conversation.return_value = ([], False, 0)

        message = MagicMock()
        message.author = MagicMock()
        message.mentions = [bot.user]
        message.content = f"<@{bot.user.id}> what is a den?"
        message.reply = AsyncMock()

        await bot.on_message(message)

        call_args = mock_chatbot.generate_response.call_args
        assert call_args[0][0] == "what is a den?"

    @patch("denbot.bot.client.format_message_coversation", new_callable=AsyncMock)
    @patch("denbot.bot.client.format_attachment_data")
    async def test_error_sends_to_channel(
        self, mock_attachments, mock_conversation, bot_and_mocks
    ):
        bot, mock_chatbot, mock_db = bot_and_mocks
        mock_attachments.return_value = []
        mock_conversation.return_value = ([], False, 0)
        mock_chatbot.generate_response = AsyncMock(
            side_effect=Exception("something broke")
        )

        message = MagicMock()
        message.author = MagicMock()
        message.mentions = [bot.user]
        message.content = f"<@{bot.user.id}> hello"
        message.channel.send = AsyncMock()

        await bot.on_message(message)

        message.channel.send.assert_called_once()
        assert "something broke" in message.channel.send.call_args[0][0]


class TestClose:
    async def test_close_calls_db_close(self, bot_and_mocks):
        bot, _, mock_db = bot_and_mocks
        with patch.object(discord.Client, "close", new_callable=AsyncMock):
            await bot.close()
        mock_db.close.assert_called_once()

    async def test_close_still_closes_discord_on_db_error(self, bot_and_mocks):
        bot, _, mock_db = bot_and_mocks
        mock_db.close.side_effect = Exception("pool error")
        with patch.object(
            discord.Client, "close", new_callable=AsyncMock
        ) as mock_super_close:
            await bot.close()
        mock_super_close.assert_called_once()


class TestCreateBot:
    @patch("denbot.bot.client.register_points_commands")
    def test_returns_mybot_instance(self, mock_register):
        bot = create_bot(MagicMock(), MagicMock(), MagicMock())
        assert isinstance(bot, MyBot)
