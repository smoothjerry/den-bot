from unittest.mock import AsyncMock, MagicMock

import pytest
import discord

from points.commands import register_points_commands


@pytest.fixture
def commands_setup():
    """Register commands on a mock bot and return the callbacks + mocked repo."""
    mock_points_repo = MagicMock()

    registered_commands = {}

    mock_bot = MagicMock()

    def fake_command(**kwargs):
        def decorator(func):
            registered_commands[kwargs["name"]] = func
            return func
        return decorator

    mock_bot.tree.command = fake_command

    register_points_commands(mock_bot, mock_points_repo)

    return registered_commands, mock_points_repo


def _make_interaction():
    interaction = MagicMock(spec=discord.Interaction)
    interaction.response = MagicMock()
    interaction.response.send_message = AsyncMock()
    return interaction


def _make_member(user_id=123, name="user#0001", display_name="User"):
    member = MagicMock(spec=discord.Member)
    member.id = user_id
    member.__str__ = MagicMock(return_value=name)
    member.display_name = display_name
    member.mention = f"<@{user_id}>"
    return member


class TestUpdatePoints:
    async def test_positive_points(self, commands_setup):
        commands, mock_repo = commands_setup
        mock_repo.update_points.return_value = 10
        interaction = _make_interaction()
        member = _make_member()

        await commands["updatepoints"](interaction, member, 10)

        response = interaction.response.send_message.call_args[0][0]
        assert "Added" in response
        assert "10 points" in response

    async def test_negative_points(self, commands_setup):
        commands, mock_repo = commands_setup
        mock_repo.update_points.return_value = 45
        interaction = _make_interaction()
        member = _make_member()

        await commands["updatepoints"](interaction, member, -5)

        response = interaction.response.send_message.call_args[0][0]
        assert "Subtracted" in response
        assert "5 points" in response

    async def test_error_handling(self, commands_setup):
        commands, mock_repo = commands_setup
        mock_repo.update_points.side_effect = Exception("db error")
        interaction = _make_interaction()
        member = _make_member()

        await commands["updatepoints"](interaction, member, 10)

        response = interaction.response.send_message.call_args[0][0]
        assert "error" in response.lower()
        assert "db error" in response


class TestLeaderboard:
    async def test_empty_leaderboard(self, commands_setup):
        commands, mock_repo = commands_setup
        mock_repo.get_leaderboard.return_value = []
        interaction = _make_interaction()

        await commands["leaderboard"](interaction)

        response = interaction.response.send_message.call_args[0][0]
        assert "No points have been awarded yet!" in response

    async def test_populated_leaderboard(self, commands_setup):
        commands, mock_repo = commands_setup
        mock_repo.get_leaderboard.return_value = [(1, 100), (2, 50)]
        interaction = _make_interaction()

        await commands["leaderboard"](interaction)

        response = interaction.response.send_message.call_args[0][0]
        assert "Leaderboard" in response
        assert "<@1>: 100 points" in response
        assert "<@2>: 50 points" in response

    async def test_error_handling(self, commands_setup):
        commands, mock_repo = commands_setup
        mock_repo.get_leaderboard.side_effect = Exception("db error")
        interaction = _make_interaction()

        await commands["leaderboard"](interaction)

        response = interaction.response.send_message.call_args[0][0]
        assert "error" in response.lower()
        assert "db error" in response
