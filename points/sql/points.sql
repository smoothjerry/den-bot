-- name: get_user_points :one
SELECT points FROM points WHERE user_id = :user_id;

-- name: update_user_points :affected
UPDATE points SET points = :points, display_name = :display_name WHERE user_id = :user_id;

-- name: insert_user :exec
INSERT INTO points (user_id, username, display_name, points) VALUES (:user_id, :username, :display_name, :points);

-- name: get_leaderboard :many
SELECT user_id, points FROM points ORDER BY points DESC;
