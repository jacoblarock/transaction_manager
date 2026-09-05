import os
import pytest
from unittest import mock

from utils import db


def _mock_conn(rowcount=0, fetchall=None):
    conn = mock.MagicMock()
    cursor = mock.MagicMock()
    cursor.rowcount = rowcount
    if fetchall is not None:
        cursor.fetchall.return_value = fetchall
    conn.cursor.return_value.__enter__.return_value = cursor
    return conn, cursor


def test_connect_missing_password_raises(monkeypatch):
    monkeypatch.delenv("DB_PASSWORD", raising=False)
    with pytest.raises(EnvironmentError):
        db.connect()


def test_connect_calls_psycopg2_with_env(monkeypatch):
    monkeypatch.setenv("DB_USER", "testuser")
    monkeypatch.setenv("DB_PASSWORD", "testpass")
    with mock.patch("utils.db.psycopg2.connect") as mock_connect:
        db.connect()
        mock_connect.assert_called_once()
        _, kwargs = mock_connect.call_args
        assert kwargs["user"] == "testuser"
        assert kwargs["password"] == "testpass"
        assert kwargs["dbname"] == "transaction_manager"
        assert kwargs["host"] == "db"
        assert kwargs["port"] == 5432


def test_execute_returns_rowcount():
    conn, cursor = _mock_conn(rowcount=3)
    result = db.execute(conn, "delete from users where true")
    assert result == 3
    cursor.execute.assert_called_once_with("delete from users where true")


def test_select_returns_rows():
    rows = [{"u_id": 1}, {"u_id": 2}]
    conn, cursor = _mock_conn(fetchall=rows)
    result = db.select(conn, "select * from users")
    assert result == rows
    cursor.execute.assert_called_once()


@mock.patch("utils.db.execute_values")
def test_insert_single_row(mock_execute_values):
    conn, cursor = _mock_conn()
    mock_execute_values.return_value = [{"u_id": 1}]
    rows = [{"u_name": "alice", "u_pass": "hash123"}]
    result = db.insert(conn, "users", rows, primary_key="u_id")
    assert result == [1]
    mock_execute_values.assert_called_once()
    query = mock_execute_values.call_args[0][1]
    assert "INSERT INTO users" in query
    assert "u_name" in query
    assert "u_pass" in query
    assert "RETURNING u_id" in query


@mock.patch("utils.db.execute_values")
def test_insert_multiple_rows(mock_execute_values):
    conn, cursor = _mock_conn()
    mock_execute_values.return_value = [{"u_id": 1}, {"u_id": 2}]
    rows = [
        {"u_name": "alice", "u_pass": "hash1"},
        {"u_name": "bob", "u_pass": "hash2"},
    ]
    result = db.insert(conn, "users", rows, primary_key="u_id")
    assert result == [1, 2]
    mock_execute_values.assert_called_once()


def test_insert_empty_rows_returns_empty_list():
    conn = mock.MagicMock()
    result = db.insert(conn, "users", [], primary_key="u_id")
    assert result == []
    conn.cursor.assert_not_called()


@mock.patch("utils.db.execute_batch")
def test_update_single_row(mock_execute_batch):
    conn, cursor = _mock_conn(rowcount=1)
    result = db.update(
        conn,
        "users",
        {"u_pass": "newhash"},
        [{"u_id": 5}],
    )
    assert result == 1
    mock_execute_batch.assert_called_once()
    query = mock_execute_batch.call_args[0][1]
    assert "UPDATE users" in query
    assert "SET" in query
    assert "WHERE" in query
    assert "u_pass = %s" in query
    assert "u_id = %s" in query


@mock.patch("utils.db.execute_batch")
def test_update_multiple_where_rows(mock_execute_batch):
    conn, cursor = _mock_conn(rowcount=3)
    result = db.update(
        conn,
        "sessions",
        {"s_expires": "2025-01-01"},
        [{"s_u_ref": 1}, {"s_u_ref": 2}, {"s_u_ref": 3}],
    )
    assert result == 3
    mock_execute_batch.assert_called_once()


def test_update_empty_where_returns_zero():
    conn = mock.MagicMock()
    result = db.update(conn, "users", {"u_pass": "x"}, [])
    assert result == 0
    conn.cursor.assert_not_called()


@mock.patch("utils.db.execute_batch")
def test_delete_single_row(mock_execute_batch):
    conn, cursor = _mock_conn(rowcount=1)
    result = db.delete(conn, "sessions", [{"s_token": "abc"}])
    assert result == 1
    mock_execute_batch.assert_called_once()
    query = mock_execute_batch.call_args[0][1]
    assert "DELETE FROM sessions" in query
    assert "s_token = %s" in query


@mock.patch("utils.db.execute_batch")
def test_delete_multiple_rows(mock_execute_batch):
    conn, cursor = _mock_conn(rowcount=2)
    result = db.delete(conn, "users", [{"u_id": 1}, {"u_id": 2}])
    assert result == 2
    mock_execute_batch.assert_called_once()


def test_delete_empty_rows_returns_zero():
    conn = mock.MagicMock()
    result = db.delete(conn, "users", [])
    assert result == 0
    conn.cursor.assert_not_called()
