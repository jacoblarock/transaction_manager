from unittest import mock

import utils.payments as payments


@mock.patch("utils.payments.check_auth")
@mock.patch("utils.payments.db")
def test_create_payment(mock_db, mock_check_auth):
    mock_check_auth.return_value = 5
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.return_value = [{"row_count": 1}]
    mock_db.insert.return_value = [42]
    result = payments.create_payment("token", 7, 9, 25.00)
    assert result == 42
    mock_db.insert.assert_called_once()
    insert_args = mock_db.insert.call_args
    assert insert_args[0][1] == "payments"
    inserted_row = insert_args[0][2][0]
    assert inserted_row["p_u_sender"] == 5
    assert inserted_row["p_u_recipient"] == 9
    assert inserted_row["p_g_ref"] == 7
    assert inserted_row["p_amount"] == 25.00
    assert insert_args[1]["primary_key"] == "p_id"


@mock.patch("utils.payments.check_auth")
@mock.patch("utils.payments.db")
def test_create_payment_not_member(mock_db, mock_check_auth):
    mock_check_auth.return_value = 5
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.return_value = [{"row_count": 0}]
    result = payments.create_payment("token", 7, 9, 25.00)
    assert result == -1
    mock_db.insert.assert_not_called()


@mock.patch("utils.payments.check_auth")
@mock.patch("utils.payments.db")
def test_delete_payment(mock_db, mock_check_auth):
    mock_check_auth.return_value = 5
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.side_effect = [
        [{"p_g_ref": 7, "p_u_sender": 5}],
        [{"row_count": 1}],
    ]
    result = payments.delete_payment("token", 42)
    assert result is True
    mock_db.delete.assert_called_once()
    delete_args = mock_db.delete.call_args
    assert delete_args[0][1] == "payments"
    assert delete_args[0][2] == [{"p_id": 42}]


@mock.patch("utils.payments.check_auth")
@mock.patch("utils.payments.db")
def test_delete_payment_not_found(mock_db, mock_check_auth):
    mock_check_auth.return_value = 5
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.return_value = []
    result = payments.delete_payment("token", 42)
    assert result is False
    mock_db.delete.assert_not_called()


@mock.patch("utils.payments.check_auth")
@mock.patch("utils.payments.db")
def test_delete_payment_not_member(mock_db, mock_check_auth):
    mock_check_auth.return_value = 5
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.side_effect = [
        [{"p_g_ref": 7, "p_u_sender": 5}],
        [{"row_count": 0}],
    ]
    result = payments.delete_payment("token", 42)
    assert result is False
    mock_db.delete.assert_not_called()


@mock.patch("utils.payments.check_auth")
@mock.patch("utils.payments.db")
def test_update_payment(mock_db, mock_check_auth):
    mock_check_auth.return_value = 5
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.side_effect = [
        [{"p_g_ref": 7}],
        [{"row_count": 1}],
    ]
    result = payments.update_payment("token", 42, 30.00)
    assert result is True
    mock_db.update.assert_called_once()
    update_args = mock_db.update.call_args
    assert update_args[0][1] == "payments"
    assert update_args[0][2] == {"p_amount": 30.00}
    assert update_args[0][3] == [{"p_id": 42}]


@mock.patch("utils.payments.check_auth")
@mock.patch("utils.payments.db")
def test_update_payment_not_found(mock_db, mock_check_auth):
    mock_check_auth.return_value = 5
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.return_value = []
    result = payments.update_payment("token", 42, 30.00)
    assert result is False
    mock_db.update.assert_not_called()


@mock.patch("utils.payments.check_auth")
@mock.patch("utils.payments.db")
def test_update_payment_not_member(mock_db, mock_check_auth):
    mock_check_auth.return_value = 5
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.side_effect = [
        [{"p_g_ref": 7}],
        [{"row_count": 0}],
    ]
    result = payments.update_payment("token", 42, 30.00)
    assert result is False
    mock_db.update.assert_not_called()


@mock.patch("utils.payments.check_auth")
@mock.patch("utils.payments.db")
def test_get_payments(mock_db, mock_check_auth):
    mock_check_auth.return_value = 5
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.side_effect = [
        [{"row_count": 1}],
        [{"p_id": 1, "p_u_sender": 5, "p_u_recipient": 9, "p_g_ref": 7, "p_amount": 25.00}],
    ]
    result = payments.get_payments("token", 7)
    assert result == [{"p_id": 1, "p_u_sender": 5, "p_u_recipient": 9, "p_g_ref": 7, "p_amount": 25.00}]
    assert mock_db.select.call_count == 2


@mock.patch("utils.payments.check_auth")
@mock.patch("utils.payments.db")
def test_get_payments_not_member(mock_db, mock_check_auth):
    mock_check_auth.return_value = 5
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.return_value = [{"row_count": 0}]
    result = payments.get_payments("token", 7)
    assert result == []
    assert mock_db.select.call_count == 1
