CREATE TABLE IF NOT EXISTS points (
    user_id BIGINT PRIMARY KEY,
    username TEXT NOT NULL,
    display_name TEXT NOT NULL,
    points INTEGER NOT NULL DEFAULT 0
);
