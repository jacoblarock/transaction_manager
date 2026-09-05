from string import ascii_uppercase, digits
from unittest import mock

import utils.auth as auth


def test_gen_session_token_length():
    token = auth.gen_session_token()
    assert len(token) == 100


def test_gen_session_token_charset():
    token = auth.gen_session_token()
    allowed = set(ascii_uppercase + digits)
    assert set(token).issubset(allowed)


def test_gen_session_token_is_string():
    token = auth.gen_session_token()
    assert isinstance(token, str)


def test_gen_session_token_uniqueness():
    tokens = {auth.gen_session_token() for _ in range(100)}
    assert len(tokens) == 100


@mock.patch("utils.auth.db")
def test_check_auth_success(mock_db):
    mock_conn = mock.MagicMock()
    mock_db.connect.return_value.__enter__.return_value = mock_conn
    mock_db.select.return_value = [{"s_u_ref": 42}]
    result = auth.check_auth("valid_token")
    assert result == 42


@mock.patch("utils.auth.db")
def test_check_auth_no_session(mock_db):
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.return_value = []
    result = auth.check_auth("invalid_token")
    assert result == -1


@mock.patch("utils.auth.db")
def test_check_auth_multiple_sessions(mock_db):
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.return_value = [{"s_u_ref": 1}, {"s_u_ref": 2}]
    result = auth.check_auth("ambiguous_token")
    assert result == -1


@mock.patch("utils.auth.db")
def test_check_auth_null_u_ref(mock_db):
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.return_value = [{"s_u_ref": None}]
    result = auth.check_auth("null_token")
    assert result == -1


@mock.patch("utils.auth.db")
def test_check_invite_token_success(mock_db):
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.return_value = [{"it_id": 7}]
    result = auth.check_invite_token("valid_invite")
    assert result == 7


@mock.patch("utils.auth.db")
def test_check_invite_token_not_found(mock_db):
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.return_value = []
    result = auth.check_invite_token("bad_invite")
    assert result == -1


@mock.patch("utils.auth.db")
def test_check_invite_token_multiple(mock_db):
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.return_value = [{"it_id": 1}, {"it_id": 2}]
    result = auth.check_invite_token("ambiguous_invite")
    assert result == -1


@mock.patch("utils.auth.db")
def test_authenticate_user_not_found(mock_db):
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.return_value = []
    result = auth.authenticate("ghost", "hash")
    assert result == ("user not found", 400)


@mock.patch("utils.auth.db")
def test_authenticate_password_match(mock_db):
    mock_conn = mock.MagicMock()
    mock_db.connect.return_value.__enter__.return_value = mock_conn
    mock_db.select.side_effect = [
        [{"u_id": 1}],
        [{"u_pass": "correct_hash"}],
    ]
    result = auth.authenticate("alice", "correct_hash")
    assert result[1] == 200
    assert len(result[0]) == 100
    mock_db.insert.assert_called_once()
    insert_args = mock_db.insert.call_args
    assert insert_args[0][1] == "sessions"


@mock.patch("utils.auth.db")
def test_authenticate_password_mismatch(mock_db):
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.side_effect = [
        [{"u_id": 1}],
        [{"u_pass": "db_hash"}],
    ]
    result = auth.authenticate("alice", "wrong_hash")
    assert result == ("password does not match", 400)


@mock.patch("utils.auth.db")
def test_authenticate_multiple_users(mock_db):
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.return_value = [{"u_id": 1}, {"u_id": 2}]
    result = auth.authenticate("alice", "hash")
    assert result == ("user not found", 400)
