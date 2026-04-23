from pathlib import Path
from typing import Any

import aiosql

from denbot.db.connection import Database

queries = aiosql.from_path(Path(__file__).parent / "sql", "psycopg2")


class PointsRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def update_points(
        self, user_id: int, username: str, display_name: str, points: int
    ) -> int:
        """
        Add or subtract points for a user. Inserts the user if they don't exist.

        Returns the new point total.
        """
        with self.db.connection() as conn:
            result = queries.get_user_points(conn, user_id=user_id)

            if result:
                new_points = result[0] + points
                queries.update_user_points(
                    conn, points=new_points, display_name=display_name, user_id=user_id
                )
            else:
                new_points = points
                queries.insert_user(
                    conn,
                    user_id=user_id,
                    username=username,
                    display_name=display_name,
                    points=new_points,
                )

        return new_points

    def get_leaderboard(self) -> list[Any]:
        """
        Returns list of (user_id, points) tuples ordered by points descending.
        """
        with self.db.connection() as conn:
            return queries.get_leaderboard(conn)
