from unittest import mock

import utils.transactions as transactions


@mock.patch("utils.transactions.check_auth")
@mock.patch("utils.transactions.db")
def test_create_transaction(mock_db, mock_check_auth):
    mock_check_auth.return_value = 5
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.return_value = [{"row_count": 1}]
    mock_db.insert.return_value = [42]
    result = transactions.create_transaction("token", 7, "lunch", 12.50)
    assert result == 42
    mock_db.insert.assert_called_once()
    insert_args = mock_db.insert.call_args
    assert insert_args[0][1] == "transactions"
    inserted_row = insert_args[0][2][0]
    assert inserted_row["t_u_ref"] == 5
    assert inserted_row["t_name"] == "lunch"
    assert inserted_row["t_g_ref"] == 7
    assert inserted_row["t_amount"] == 12.50
    assert "t_date" not in inserted_row
    assert insert_args[1]["primary_key"] == "t_id"


@mock.patch("utils.transactions.check_auth")
@mock.patch("utils.transactions.db")
def test_create_transaction_with_date(mock_db, mock_check_auth):
    mock_check_auth.return_value = 5
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.return_value = [{"row_count": 1}]
    mock_db.insert.return_value = [42]
    result = transactions.create_transaction("token", 7, "lunch", 12.50, "2026-09-01")
    assert result == 42
    insert_args = mock_db.insert.call_args
    inserted_row = insert_args[0][2][0]
    assert inserted_row["t_date"] == "2026-09-01"
    assert insert_args[1]["primary_key"] == "t_id"


@mock.patch("utils.transactions.check_auth")
@mock.patch("utils.transactions.db")
def test_create_transaction_not_member(mock_db, mock_check_auth):
    mock_check_auth.return_value = 5
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.return_value = [{"row_count": 0}]
    result = transactions.create_transaction("token", 7, "lunch", 12.50)
    assert result == -1
    mock_db.insert.assert_not_called()


@mock.patch("utils.transactions.check_auth")
@mock.patch("utils.transactions.db")
def test_delete_transaction(mock_db, mock_check_auth):
    mock_check_auth.return_value = 5
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.side_effect = [
        [{"t_g_ref": 7}],
        [{"row_count": 1}],
    ]
    result = transactions.delete_transaction("token", 42)
    assert result is True
    mock_db.delete.assert_called_once()
    delete_args = mock_db.delete.call_args
    assert delete_args[0][1] == "transactions"
    assert delete_args[0][2] == [{"t_id": 42}]


@mock.patch("utils.transactions.check_auth")
@mock.patch("utils.transactions.db")
def test_delete_transaction_not_found(mock_db, mock_check_auth):
    mock_check_auth.return_value = 5
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.return_value = []
    result = transactions.delete_transaction("token", 42)
    assert result is False
    mock_db.delete.assert_not_called()


@mock.patch("utils.transactions.check_auth")
@mock.patch("utils.transactions.db")
def test_delete_transaction_not_member(mock_db, mock_check_auth):
    mock_check_auth.return_value = 5
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.side_effect = [
        [{"t_g_ref": 7}],
        [{"row_count": 0}],
    ]
    result = transactions.delete_transaction("token", 42)
    assert result is False
    mock_db.delete.assert_not_called()


@mock.patch("utils.transactions.check_auth")
@mock.patch("utils.transactions.db")
def test_update_transaction(mock_db, mock_check_auth):
    mock_check_auth.return_value = 5
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.side_effect = [
        [{"t_g_ref": 7}],
        [{"row_count": 1}],
    ]
    result = transactions.update_transaction("token", 42, "dinner", 25.00)
    assert result is True
    mock_db.update.assert_called_once()
    update_args = mock_db.update.call_args
    assert update_args[0][1] == "transactions"
    assert update_args[0][2] == {"t_name": "dinner", "t_amount": 25.00}
    assert update_args[0][3] == [{"t_id": 42}]


@mock.patch("utils.transactions.check_auth")
@mock.patch("utils.transactions.db")
def test_update_transaction_not_found(mock_db, mock_check_auth):
    mock_check_auth.return_value = 5
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.return_value = []
    result = transactions.update_transaction("token", 42, "dinner", 25.00)
    assert result is False
    mock_db.update.assert_not_called()


@mock.patch("utils.transactions.check_auth")
@mock.patch("utils.transactions.db")
def test_update_transaction_not_member(mock_db, mock_check_auth):
    mock_check_auth.return_value = 5
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.side_effect = [
        [{"t_g_ref": 7}],
        [{"row_count": 0}],
    ]
    result = transactions.update_transaction("token", 42, "dinner", 25.00)
    assert result is False
    mock_db.update.assert_not_called()


@mock.patch("utils.transactions.check_auth")
@mock.patch("utils.transactions.db")
def test_get_transactions(mock_db, mock_check_auth):
    mock_check_auth.return_value = 5
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.side_effect = [
        [{"row_count": 1}],
        [{"t_id": 1, "t_u_ref": 5, "t_name": "lunch", "t_g_ref": 7, "t_amount": 12.50}],
    ]
    result = transactions.get_transactions("token", 7)
    assert result == [{"t_id": 1, "t_u_ref": 5, "t_name": "lunch", "t_g_ref": 7, "t_amount": 12.50}]
    assert mock_db.select.call_count == 2


@mock.patch("utils.transactions.check_auth")
@mock.patch("utils.transactions.db")
def test_get_transactions_not_member(mock_db, mock_check_auth):
    mock_check_auth.return_value = 5
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.return_value = [{"row_count": 0}]
    result = transactions.get_transactions("token", 7)
    assert result == []
    assert mock_db.select.call_count == 1
