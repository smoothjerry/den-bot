from unittest.mock import MagicMock, patch

from denbot.db.connection import Database


class TestDatabase:
    @patch("denbot.db.connection.SimpleConnectionPool")
    def test_connection_yields_and_returns(self, mock_pool_cls):
        mock_pool = MagicMock()
        mock_conn = MagicMock()
        mock_conn.closed = 0
        mock_pool.getconn.return_value = mock_conn
        mock_pool_cls.return_value = mock_pool

        db = Database("postgres://fake")

        with db.connection() as conn:
            assert conn is mock_conn

        mock_pool.getconn.assert_called_once()
        mock_pool.putconn.assert_called_once_with(mock_conn)

    @patch("denbot.db.connection.SimpleConnectionPool")
    def test_close_calls_closeall(self, mock_pool_cls):
        mock_pool = MagicMock()
        mock_pool_cls.return_value = mock_pool

        db = Database("postgres://fake")
        db.close()

        mock_pool.closeall.assert_called_once()
