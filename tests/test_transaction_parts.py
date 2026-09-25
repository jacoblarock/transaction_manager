from unittest import mock

import utils.transaction_parts as transaction_parts


@mock.patch("utils.transaction_parts.check_auth")
@mock.patch("utils.transaction_parts.db")
def test_create_transaction_part(mock_db, mock_check_auth):
    mock_check_auth.return_value = 5
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.side_effect = [
        [{"t_g_ref": 7, "t_amount": "60.00"}],
        [{"row_count": 1}],
        [{"total": "20.00"}],
    ]
    mock_db.insert.return_value = [42]
    result = transaction_parts.create_transaction_part("token", 1, 9, 20.00)
    assert result == 42
    mock_db.insert.assert_called_once()
    insert_args = mock_db.insert.call_args
    assert insert_args[0][1] == "transaction_parts"
    inserted_row = insert_args[0][2][0]
    assert inserted_row["tp_t_ref"] == 1
    assert inserted_row["tp_u_ref"] == 9
    assert inserted_row["tp_amount"] == 20.00
    assert insert_args[1]["primary_key"] == "tp_id"


@mock.patch("utils.transaction_parts.check_auth")
@mock.patch("utils.transaction_parts.db")
def test_create_transaction_part_exceeds_total(mock_db, mock_check_auth):
    mock_check_auth.return_value = 5
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.side_effect = [
        [{"t_g_ref": 7, "t_amount": "60.00"}],
        [{"row_count": 1}],
        [{"total": "50.00"}],
    ]
    result = transaction_parts.create_transaction_part("token", 1, 9, 20.00)
    assert result == -2
    mock_db.insert.assert_not_called()


@mock.patch("utils.transaction_parts.check_auth")
@mock.patch("utils.transaction_parts.db")
def test_create_transaction_part_not_member(mock_db, mock_check_auth):
    mock_check_auth.return_value = 5
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.side_effect = [
        [{"t_g_ref": 7, "t_amount": "60.00"}],
        [{"row_count": 0}],
    ]
    result = transaction_parts.create_transaction_part("token", 1, 9, 20.00)
    assert result == -1
    mock_db.insert.assert_not_called()


@mock.patch("utils.transaction_parts.check_auth")
@mock.patch("utils.transaction_parts.db")
def test_create_transaction_part_transaction_not_found(mock_db, mock_check_auth):
    mock_check_auth.return_value = 5
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.return_value = []
    result = transaction_parts.create_transaction_part("token", 1, 9, 20.00)
    assert result == -1
    mock_db.insert.assert_not_called()


@mock.patch("utils.transaction_parts.check_auth")
@mock.patch("utils.transaction_parts.db")
def test_delete_transaction_part(mock_db, mock_check_auth):
    mock_check_auth.return_value = 5
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.side_effect = [
        [{"tp_t_ref": 1}],
        [{"t_g_ref": 7}],
        [{"row_count": 1}],
    ]
    result = transaction_parts.delete_transaction_part("token", 42)
    assert result is True
    mock_db.delete.assert_called_once()
    delete_args = mock_db.delete.call_args
    assert delete_args[0][1] == "transaction_parts"
    assert delete_args[0][2] == [{"tp_id": 42}]


@mock.patch("utils.transaction_parts.check_auth")
@mock.patch("utils.transaction_parts.db")
def test_delete_transaction_part_not_found(mock_db, mock_check_auth):
    mock_check_auth.return_value = 5
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.return_value = []
    result = transaction_parts.delete_transaction_part("token", 42)
    assert result is False
    mock_db.delete.assert_not_called()


@mock.patch("utils.transaction_parts.check_auth")
@mock.patch("utils.transaction_parts.db")
def test_delete_transaction_part_not_member(mock_db, mock_check_auth):
    mock_check_auth.return_value = 5
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.side_effect = [
        [{"tp_t_ref": 1}],
        [{"t_g_ref": 7}],
        [{"row_count": 0}],
    ]
    result = transaction_parts.delete_transaction_part("token", 42)
    assert result is False
    mock_db.delete.assert_not_called()


@mock.patch("utils.transaction_parts.check_auth")
@mock.patch("utils.transaction_parts.db")
def test_update_transaction_part(mock_db, mock_check_auth):
    mock_check_auth.return_value = 5
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.side_effect = [
        [{"tp_t_ref": 1}],
        [{"t_g_ref": 7, "t_amount": "60.00"}],
        [{"row_count": 1}],
        [{"total": "20.00"}],
    ]
    result = transaction_parts.update_transaction_part("token", 42, 9, 30.00)
    assert result is True
    mock_db.update.assert_called_once()
    update_args = mock_db.update.call_args
    assert update_args[0][1] == "transaction_parts"
    assert update_args[0][2] == {"tp_u_ref": 9, "tp_amount": 30.00}
    assert update_args[0][3] == [{"tp_id": 42}]


@mock.patch("utils.transaction_parts.check_auth")
@mock.patch("utils.transaction_parts.db")
def test_update_transaction_part_exceeds_total(mock_db, mock_check_auth):
    mock_check_auth.return_value = 5
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.side_effect = [
        [{"tp_t_ref": 1}],
        [{"t_g_ref": 7, "t_amount": "60.00"}],
        [{"row_count": 1}],
        [{"total": "50.00"}],
    ]
    result = transaction_parts.update_transaction_part("token", 42, 9, 20.00)
    assert result == -2
    mock_db.update.assert_not_called()


@mock.patch("utils.transaction_parts.check_auth")
@mock.patch("utils.transaction_parts.db")
def test_update_transaction_part_not_found(mock_db, mock_check_auth):
    mock_check_auth.return_value = 5
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.return_value = []
    result = transaction_parts.update_transaction_part("token", 42, 9, 30.00)
    assert result is False
    mock_db.update.assert_not_called()


@mock.patch("utils.transaction_parts.check_auth")
@mock.patch("utils.transaction_parts.db")
def test_update_transaction_part_not_member(mock_db, mock_check_auth):
    mock_check_auth.return_value = 5
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.side_effect = [
        [{"tp_t_ref": 1}],
        [{"t_g_ref": 7, "t_amount": "60.00"}],
        [{"row_count": 0}],
    ]
    result = transaction_parts.update_transaction_part("token", 42, 9, 30.00)
    assert result is False
    mock_db.update.assert_not_called()


@mock.patch("utils.transaction_parts.check_auth")
@mock.patch("utils.transaction_parts.db")
def test_get_transaction_parts(mock_db, mock_check_auth):
    mock_check_auth.return_value = 5
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.side_effect = [
        [{"t_g_ref": 7}],
        [{"row_count": 1}],
        [{"tp_id": 1, "tp_t_ref": 1, "tp_u_ref": 9, "tp_amount": "20.00"}],
    ]
    result = transaction_parts.get_transaction_parts("token", 1)
    assert result == [{"tp_id": 1, "tp_t_ref": 1, "tp_u_ref": 9, "tp_amount": "20.00"}]
    assert mock_db.select.call_count == 3


@mock.patch("utils.transaction_parts.check_auth")
@mock.patch("utils.transaction_parts.db")
def test_get_transaction_parts_not_member(mock_db, mock_check_auth):
    mock_check_auth.return_value = 5
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.side_effect = [
        [{"t_g_ref": 7}],
        [{"row_count": 0}],
    ]
    result = transaction_parts.get_transaction_parts("token", 1)
    assert result == []
    assert mock_db.select.call_count == 2


@mock.patch("utils.transaction_parts.check_auth")
@mock.patch("utils.transaction_parts.db")
def test_get_transaction_parts_transaction_not_found(mock_db, mock_check_auth):
    mock_check_auth.return_value = 5
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.return_value = []
    result = transaction_parts.get_transaction_parts("token", 1)
    assert result == []
    assert mock_db.select.call_count == 1
