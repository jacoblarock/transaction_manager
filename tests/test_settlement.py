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
        [{"t_id": 1, "t_u_ref": 1, "t_amount": 100.0}],
        [],
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
        [{"t_id": 1, "t_u_ref": 1, "t_amount": 100.0}],
        [],
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
            {"t_id": 1, "t_u_ref": 1, "t_amount": 60.0},
            {"t_id": 2, "t_u_ref": 2, "t_amount": 30.0},
        ],
        [],
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
        [{"t_id": 1, "t_u_ref": 1, "t_amount": 100.0}],
        [],
        [{"p_u_sender": 2, "p_u_recipient": 1, "p_amount": 50.0}],
    ]
    result = settlement.settle_balances("token", 7)
    assert result == []


@mock.patch("utils.settlement.check_auth")
@mock.patch("utils.settlement.db")
def test_settle_balances_with_parts(mock_db, mock_check_auth):
    mock_check_auth.return_value = 5
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.side_effect = [
        [{"row_count": 1}],
        [{"ugm_u_ref": 1}, {"ugm_u_ref": 2}],
        [{"t_id": 1, "t_u_ref": 1, "t_amount": 100.0}],
        [{"tp_t_ref": 1, "tp_u_ref": 2, "tp_amount": 60.0}],
        [],
    ]
    result = settlement.settle_balances("token", 7)
    # user1 paid 100, 60 attributed to user2, remainder 40 split evenly (20 each)
    # user1: 100 - 20 = 80; user2: -60 - 20 = -80
    assert len(result) == 1
    assert result[0]["from"] == 2
    assert result[0]["to"] == 1
    assert result[0]["amount"] == 80.0


@mock.patch("utils.settlement.check_auth")
@mock.patch("utils.settlement.db")
def test_settle_balances_parts_full_amount(mock_db, mock_check_auth):
    mock_check_auth.return_value = 5
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.side_effect = [
        [{"row_count": 1}],
        [{"ugm_u_ref": 1}, {"ugm_u_ref": 2}, {"ugm_u_ref": 3}],
        [{"t_id": 1, "t_u_ref": 1, "t_amount": 90.0}],
        [
            {"tp_t_ref": 1, "tp_u_ref": 2, "tp_amount": 40.0},
            {"tp_t_ref": 1, "tp_u_ref": 3, "tp_amount": 50.0},
        ],
        [],
    ]
    result = settlement.settle_balances("token", 7)
    # user1 paid 90; parts fully cover it (40+50=90), no remainder split
    # user1: 90; user2: -40; user3: -50
    assert len(result) == 2
    transfers = {(t["from"], t["to"]): t["amount"] for t in result}
    assert transfers[(2, 1)] == 40.0
    assert transfers[(3, 1)] == 50.0


@mock.patch("utils.settlement.check_auth")
@mock.patch("utils.settlement.db")
def test_settle_balances_parts_with_payment(mock_db, mock_check_auth):
    mock_check_auth.return_value = 5
    mock_db.connect.return_value.__enter__.return_value = mock.MagicMock()
    mock_db.select.side_effect = [
        [{"row_count": 1}],
        [{"ugm_u_ref": 1}, {"ugm_u_ref": 2}],
        [{"t_id": 1, "t_u_ref": 1, "t_amount": 100.0}],
        [{"tp_t_ref": 1, "tp_u_ref": 2, "tp_amount": 60.0}],
        [{"p_u_sender": 2, "p_u_recipient": 1, "p_amount": 30.0}],
    ]
    result = settlement.settle_balances("token", 7)
    # user1: 80, user2: -80; payment 30 from 2 to 1 → user1: 110-... wait
    # before payment: user1=80, user2=-80
    # payment: user2 paid user1 30 → user2 += 30 = -50, user1 -= 30 = 50
    assert len(result) == 1
    assert result[0]["from"] == 2
    assert result[0]["to"] == 1
    assert result[0]["amount"] == 50.0
