import sys
from unittest.mock import patch, MagicMock

import pytest


@pytest.fixture
def repo_and_mocks(mock_db):
    db, mock_conn = mock_db
    mock_queries = MagicMock()

    with patch.dict(sys.modules, {"denbot.points.repository": None}):
        with patch("aiosql.from_path", return_value=mock_queries):
            # Force re-import so aiosql.from_path is intercepted
            if "denbot.points.repository" in sys.modules:
                del sys.modules["denbot.points.repository"]

            from denbot.points.repository import PointsRepository

            repo = PointsRepository(db)
            # Bind the mock_queries to the module's queries reference
            import denbot.points.repository as repo_module
            repo_module.queries = mock_queries

            yield repo, mock_queries, mock_conn


class TestUpdatePoints:
    def test_new_user_inserts(self, repo_and_mocks):
        repo, mock_queries, mock_conn = repo_and_mocks
        mock_queries.get_user_points.return_value = None

        result = repo.update_points(123, "user#0001", "User", 10)

        mock_queries.insert_user.assert_called_once_with(
            mock_conn, user_id=123, username="user#0001", display_name="User", points=10
        )
        assert result == 10

    def test_existing_user_updates(self, repo_and_mocks):
        repo, mock_queries, mock_conn = repo_and_mocks
        mock_queries.get_user_points.return_value = (50,)

        result = repo.update_points(123, "user#0001", "User", 20)

        mock_queries.update_user_points.assert_called_once_with(
            mock_conn, points=70, display_name="User", user_id=123
        )
        assert result == 70

    def test_negative_points(self, repo_and_mocks):
        repo, mock_queries, mock_conn = repo_and_mocks
        mock_queries.get_user_points.return_value = (50,)

        result = repo.update_points(123, "user#0001", "User", -30)

        mock_queries.update_user_points.assert_called_once_with(
            mock_conn, points=20, display_name="User", user_id=123
        )
        assert result == 20

    def test_returns_new_total(self, repo_and_mocks):
        repo, mock_queries, mock_conn = repo_and_mocks
        mock_queries.get_user_points.return_value = (100,)

        result = repo.update_points(123, "user#0001", "User", 5)
        assert result == 105


class TestGetLeaderboard:
    def test_returns_rows(self, repo_and_mocks):
        repo, mock_queries, mock_conn = repo_and_mocks
        mock_queries.get_leaderboard.return_value = [(1, 100), (2, 50)]

        result = repo.get_leaderboard()
        assert result == [(1, 100), (2, 50)]

    def test_empty(self, repo_and_mocks):
        repo, mock_queries, mock_conn = repo_and_mocks
        mock_queries.get_leaderboard.return_value = []

        result = repo.get_leaderboard()
        assert result == []
