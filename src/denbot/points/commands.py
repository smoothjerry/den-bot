from typing import Any

import discord

from denbot.points.repository import PointsRepository


def register_points_commands(bot: Any, points_repo: PointsRepository) -> None:
    @bot.tree.command(
        name="updatepoints", description="Add or subtract points for a user."
    )
    async def update_points(
        interaction: discord.Interaction, member: discord.Member, points: int
    ) -> None:
        user_id = member.id
        username = str(member)
        display_name = member.display_name

        try:
            new_points = points_repo.update_points(
                user_id, username, display_name, points
            )
            action = "Added" if points > 0 else "Subtracted"
            await interaction.response.send_message(
                f"{action} {abs(points)} points to {member.mention}."
                f" Total: {new_points} points."
            )
        except Exception as e:
            await interaction.response.send_message(
                f"An error occurred while updating points: {e}"
            )

    @bot.tree.command(
        name="leaderboard", description="View the leaderboard of den points."
    )
    async def leaderboard(interaction: discord.Interaction) -> None:
        try:
            rows = points_repo.get_leaderboard()

            if not rows:
                await interaction.response.send_message(
                    "No points have been awarded yet!"
                )
                return

            leaderboard = "\n".join([f"<@{row[0]}>: {row[1]} points" for row in rows])
            await interaction.response.send_message(
                f"**Den Points Leaderboard:**\n{leaderboard}"
            )
        except Exception as e:
            await interaction.response.send_message(
                f"An error occurred while fetching the leaderboard: {e}"
            )
