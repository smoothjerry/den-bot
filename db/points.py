from db.connection import get_db_conn


class PointsRepository:
    def __init__(self, database_url):
        self.database_url = database_url

    def update_points(self, user_id, username, display_name, points):
        """
        Add or subtract points for a user. Inserts the user if they don't exist.

        Returns the new point total.
        """
        with get_db_conn(self.database_url) as conn:
            with conn.cursor() as cursor:
                cursor.execute('SELECT points FROM points WHERE user_id = %s', (user_id,))
                result = cursor.fetchone()

                if result:
                    new_points = result[0] + points
                    cursor.execute(
                        'UPDATE points SET points = %s, display_name = %s WHERE user_id = %s',
                        (new_points, display_name, user_id)
                    )
                else:
                    new_points = points
                    cursor.execute(
                        'INSERT INTO points (user_id, username, display_name, points) VALUES (%s, %s, %s, %s)',
                        (user_id, username, display_name, new_points)
                    )

        return new_points

    def get_leaderboard(self):
        """
        Returns list of (user_id, points) tuples ordered by points descending.
        """
        with get_db_conn(self.database_url) as conn:
            with conn.cursor() as cursor:
                cursor.execute('SELECT user_id, points FROM points ORDER BY points DESC')
                return cursor.fetchall()
