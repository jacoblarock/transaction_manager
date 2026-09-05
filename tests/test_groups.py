from unittest import mock

import utils.groups as groups


@mock.patch("utils.groups.check_auth")
@mock.patch("utils.groups.db")
def test_get_groups(mock_db, mock_check_auth):
    mock_check_auth.return_value = 5
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.return_value = [{"g_id": 1, "g_name": "alpha"}]
    result = groups.get_groups("token")
    assert result == [{"g_id": 1, "g_name": "alpha"}]
    mock_db.select.assert_called_once()
    query = mock_db.select.call_args[0][1]
    assert "from groups join user_group_map" in query
    assert "where ugm_u_ref = 5" in query


@mock.patch("utils.groups.check_auth")
@mock.patch("utils.groups.db")
def test_add_user_to_group_inserts_when_absent(mock_db, mock_check_auth):
    mock_check_auth.return_value = 1
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.side_effect = [
        [{"row_count": 1}],
        [{"row_count": 0}],
    ]
    mock_db.insert.return_value = [10]
    result = groups.add_user_to_group("token", 5, 7)
    assert result == 10
    mock_db.insert.assert_called_once()
    insert_args = mock_db.insert.call_args
    assert insert_args[0][1] == "user_group_map"
    inserted_row = insert_args[0][2][0]
    assert inserted_row["ugm_u_ref"] == 5
    assert inserted_row["ugm_g_ref"] == 7
    assert insert_args[1]["primary_key"] == "ugm_id"


@mock.patch("utils.groups.check_auth")
@mock.patch("utils.groups.db")
def test_add_user_to_group_caller_not_in_group(mock_db, mock_check_auth):
    mock_check_auth.return_value = 1
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.return_value = [{"row_count": 0}]
    result = groups.add_user_to_group("token", 5, 7)
    assert result == -1
    mock_db.insert.assert_not_called()


@mock.patch("utils.groups.check_auth")
@mock.patch("utils.groups.db")
def test_add_user_to_group_target_already_in_group(mock_db, mock_check_auth):
    mock_check_auth.return_value = 1
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.side_effect = [
        [{"row_count": 1}],
        [{"row_count": 1}],
    ]
    result = groups.add_user_to_group("token", 5, 7)
    assert result == -2
    mock_db.insert.assert_not_called()


@mock.patch("utils.groups.check_auth")
@mock.patch("utils.groups.db")
def test_remove_user_from_group_deletes_when_present(mock_db, mock_check_auth):
    mock_check_auth.return_value = 1
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.side_effect = [
        [{"row_count": 1}],
        [{"row_count": 1}],
    ]
    mock_db.delete.return_value = 1
    result = groups.remove_user_from_group("token", 5, 7)
    assert result == 1
    mock_db.delete.assert_called_once()
    delete_args = mock_db.delete.call_args
    assert delete_args[0][1] == "user_group_map"
    deleted_row = delete_args[0][2][0]
    assert deleted_row["ugm_u_ref"] == 5
    assert deleted_row["ugm_g_ref"] == 7


@mock.patch("utils.groups.check_auth")
@mock.patch("utils.groups.db")
def test_remove_user_from_group_caller_not_in_group(mock_db, mock_check_auth):
    mock_check_auth.return_value = 1
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.return_value = [{"row_count": 0}]
    result = groups.remove_user_from_group("token", 5, 7)
    assert result == -1
    mock_db.delete.assert_not_called()


@mock.patch("utils.groups.check_auth")
@mock.patch("utils.groups.db")
def test_remove_user_from_group_target_not_in_group(mock_db, mock_check_auth):
    mock_check_auth.return_value = 1
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.side_effect = [
        [{"row_count": 1}],
        [{"row_count": 0}],
    ]
    result = groups.remove_user_from_group("token", 5, 7)
    assert result == -2
    mock_db.delete.assert_not_called()


@mock.patch("utils.groups.check_auth")
@mock.patch("utils.groups.db")
def test_create_group(mock_db, mock_check_auth):
    mock_check_auth.return_value = 3
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.insert.return_value = [42]
    result = groups.create_group("token", "newgroup")
    assert result == 42
    assert mock_db.insert.call_count == 2
    group_insert = mock_db.insert.call_args_list[0]
    assert group_insert[0][1] == "groups"
    assert group_insert[0][2][0]["g_name"] == "newgroup"
    assert group_insert[1]["primary_key"] == "g_id"
    map_insert = mock_db.insert.call_args_list[1]
    assert map_insert[0][1] == "user_group_map"
    assert map_insert[0][2][0]["ugm_u_ref"] == 3
    assert map_insert[0][2][0]["ugm_g_ref"] == 42
    assert map_insert[1]["primary_key"] == "ugm_id"


@mock.patch("utils.groups.check_auth")
@mock.patch("utils.groups.db")
def test_delete_group(mock_db, mock_check_auth):
    mock_check_auth.return_value = 3
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.return_value = [{"row_count": 1}]
    result = groups.delete_group("token", 42)
    assert result is True
    assert mock_db.delete.call_count == 2
    first_call = mock_db.delete.call_args_list[0]
    assert first_call[0][1] == "user_group_map"
    assert first_call[0][2] == [{"ugm_g_ref": 42}]
    second_call = mock_db.delete.call_args_list[1]
    assert second_call[0][1] == "groups"
    assert second_call[0][2] == [{"g_id": 42}]


@mock.patch("utils.groups.check_auth")
@mock.patch("utils.groups.db")
def test_delete_group_not_member(mock_db, mock_check_auth):
    mock_check_auth.return_value = 3
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.return_value = [{"row_count": 0}]
    result = groups.delete_group("token", 42)
    assert result is False
    mock_db.delete.assert_not_called()
