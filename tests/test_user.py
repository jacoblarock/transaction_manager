from unittest import mock

import utils.user as user


@mock.patch("utils.user.db")
def test_create_invite_token(mock_db):
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    token = user.create_invite_token()
    assert len(token) == 100
    mock_db.insert.assert_called_once()
    insert_args = mock_db.insert.call_args
    assert insert_args[0][1] == "invite_tokens"
    inserted_row = insert_args[0][2][0]
    assert inserted_row["it_token"] == token


@mock.patch("utils.user.check_invite_token")
@mock.patch("utils.user.db")
def test_create_user_with_token_success(mock_db, mock_check_invite):
    mock_check_invite.return_value = 5
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.return_value = []
    result = user.create_user_with_token("valid_invite", "alice", "hash123")
    assert result == ("success", 200)
    mock_db.insert.assert_called_once()
    insert_args = mock_db.insert.call_args
    assert insert_args[0][1] == "users"
    inserted_row = insert_args[0][2][0]
    assert inserted_row["u_name"] == "alice"
    assert inserted_row["u_pass"] == "hash123"
    mock_db.update.assert_called_once()


@mock.patch("utils.user.check_invite_token")
@mock.patch("utils.user.db")
def test_create_user_with_token_invalid_token(mock_db, mock_check_invite):
    mock_check_invite.return_value = -1
    result = user.create_user_with_token("bad_token", "alice", "hash123")
    assert result == ("invalid invite token", 400)
    mock_db.insert.assert_not_called()


@mock.patch("utils.user.check_invite_token")
@mock.patch("utils.user.db")
def test_create_user_with_token_name_collision(mock_db, mock_check_invite):
    mock_check_invite.return_value = 5
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.return_value = [{"u_id": 1}, {"u_id": 2}]
    result = user.create_user_with_token("valid_invite", "alice", "hash123")
    assert result == ("user with username already exists", 400)
    mock_db.insert.assert_not_called()


@mock.patch("utils.user.check_invite_token")
@mock.patch("utils.user.db")
def test_create_user_with_token_no_collision(mock_db, mock_check_invite):
    mock_check_invite.return_value = 5
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.return_value = []
    result = user.create_user_with_token("valid_invite", "alice", "hash123")
    assert result == ("success", 200)
    update_args = mock_db.update.call_args
    assert update_args[0][1] == "invite_tokens"
    assert "it_expires" in update_args[0][2]
