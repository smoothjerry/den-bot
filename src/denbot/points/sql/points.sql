-- name: get_user_points^
SELECT points FROM points WHERE user_id = :user_id;

-- name: update_user_points$
UPDATE points SET points = :points, display_name = :display_name WHERE user_id = :user_id;

-- name: insert_user!
INSERT INTO points (user_id, username, display_name, points) VALUES (:user_id, :username, :display_name, :points);

-- name: get_leaderboard
SELECT user_id, points FROM points ORDER BY points DESC;
