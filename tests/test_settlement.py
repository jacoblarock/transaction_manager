from unittest import mock

import utils.settlement as settlement


@mock.patch("utils.settlement.check_auth")
@mock.patch("utils.settlement.db")
def test_settle_balances_not_member(mock_db, mock_check_auth):
    mock_check_auth.return_value = 5
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.return_value = [{"row_count": 0}]
    result = settlement.settle_balances("token", 7)
    assert result == []
    assert mock_db.select.call_count == 1


@mock.patch("utils.settlement.check_auth")
@mock.patch("utils.settlement.db")
def test_settle_balances_no_transactions(mock_db, mock_check_auth):
    mock_check_auth.return_value = 5
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.side_effect = [
        [{"row_count": 1}],
        [{"ugm_u_ref": 1}, {"ugm_u_ref": 2}],
        [],
        [],
    ]
    result = settlement.settle_balances("token", 7)
    assert result == []


@mock.patch("utils.settlement.check_auth")
@mock.patch("utils.settlement.db")
def test_settle_balances_simple(mock_db, mock_check_auth):
    mock_check_auth.return_value = 5
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.side_effect = [
        [{"row_count": 1}],
        [{"ugm_u_ref": 1}, {"ugm_u_ref": 2}],
        [{"t_u_ref": 1, "t_amount": 100.0}],
        [],
    ]
    result = settlement.settle_balances("token", 7)
    assert len(result) == 1
    assert result[0]["from"] == 2
    assert result[0]["to"] == 1
    assert result[0]["amount"] == 50.0


@mock.patch("utils.settlement.check_auth")
@mock.patch("utils.settlement.db")
def test_settle_balances_with_payment(mock_db, mock_check_auth):
    mock_check_auth.return_value = 5
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.side_effect = [
        [{"row_count": 1}],
        [{"ugm_u_ref": 1}, {"ugm_u_ref": 2}],
        [{"t_u_ref": 1, "t_amount": 100.0}],
        [{"p_u_sender": 2, "p_u_recipient": 1, "p_amount": 30.0}],
    ]
    result = settlement.settle_balances("token", 7)
    assert len(result) == 1
    assert result[0]["from"] == 2
    assert result[0]["to"] == 1
    assert result[0]["amount"] == 20.0


@mock.patch("utils.settlement.check_auth")
@mock.patch("utils.settlement.db")
def test_settle_balances_three_users(mock_db, mock_check_auth):
    mock_check_auth.return_value = 5
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.side_effect = [
        [{"row_count": 1}],
        [{"ugm_u_ref": 1}, {"ugm_u_ref": 2}, {"ugm_u_ref": 3}],
        [
            {"t_u_ref": 1, "t_amount": 60.0},
            {"t_u_ref": 2, "t_amount": 30.0},
        ],
        [],
    ]
    result = settlement.settle_balances("token", 7)
    total = 90.0
    share = total / 3
    # user 1 balance: 60 - 30 = 30 (creditor)
    # user 2 balance: 30 - 30 = 0
    # user 3 balance: 0 - 30 = -30 (debtor)
    assert len(result) == 1
    assert result[0]["from"] == 3
    assert result[0]["to"] == 1
    assert result[0]["amount"] == 30.0


@mock.patch("utils.settlement.check_auth")
@mock.patch("utils.settlement.db")
def test_settle_balances_already_settled(mock_db, mock_check_auth):
    mock_check_auth.return_value = 5
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.side_effect = [
        [{"row_count": 1}],
        [{"ugm_u_ref": 1}, {"ugm_u_ref": 2}],
        [{"t_u_ref": 1, "t_amount": 100.0}],
        [{"p_u_sender": 2, "p_u_recipient": 1, "p_amount": 50.0}],
    ]
    result = settlement.settle_balances("token", 7)
    assert result == []
