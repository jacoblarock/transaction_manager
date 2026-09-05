from unittest import mock

import pytest
import app


@pytest.fixture
def client():
    app.app.config["TESTING"] = True
    with app.app.test_client() as c:
        yield c


def test_healthcheck(client):
    response = client.get("/api/")
    assert response.status_code == 200


def test_authenticate_missing_user(client):
    response = client.get("/api/authenticate?passHash=abc123")
    assert response.status_code == 400


def test_authenticate_missing_passhash(client):
    response = client.get("/api/authenticate?user=alice")
    assert response.status_code == 400


def test_authenticate_missing_all_params(client):
    response = client.get("/api/authenticate")
    assert response.status_code == 400


@mock.patch("app.auth.authenticate")
def test_authenticate_valid_params(mock_authenticate):
    mock_authenticate.return_value = ("session_token_123", 200)
    app.app.config["TESTING"] = True
    with app.app.test_client() as c:
        response = c.get("/api/authenticate?user=alice&passHash=abc123")
    assert response.status_code == 200
    mock_authenticate.assert_called_once_with("alice", "abc123")


@mock.patch("app.auth.authenticate")
def test_authenticate_returns_error(mock_authenticate):
    mock_authenticate.return_value = ("password does not match", 400)
    app.app.config["TESTING"] = True
    with app.app.test_client() as c:
        response = c.get("/api/authenticate?user=alice&passHash=wrong")
    assert response.status_code == 400


def test_auth_check_no_token(client):
    response = client.get("/api/auth_check")
    assert response.status_code == 400


@mock.patch("app.auth.check_auth")
def test_auth_check_valid_session(mock_check_auth):
    mock_check_auth.return_value = 42
    app.app.config["TESTING"] = True
    with app.app.test_client() as c:
        response = c.get("/api/auth_check?token=valid_token")
    assert response.status_code == 200
    mock_check_auth.assert_called_once_with("valid_token")


@mock.patch("app.auth.check_auth")
def test_auth_check_session_not_found(mock_check_auth):
    mock_check_auth.return_value = -1
    app.app.config["TESTING"] = True
    with app.app.test_client() as c:
        response = c.get("/api/auth_check?token=invalid_token")
    assert response.status_code == 400


def test_create_user_missing_params(client):
    response = client.get("/api/create_user_from_invite_token")
    assert response.status_code == 400


def test_create_user_partial_params(client):
    response = client.get("/api/create_user_from_invite_token?token=abc&user=alice")
    assert response.status_code == 400


@mock.patch("app.user.create_user_with_token")
def test_create_user_valid_params(mock_create):
    mock_create.return_value = ("success", 200)
    app.app.config["TESTING"] = True
    with app.app.test_client() as c:
        response = c.get(
            "/api/create_user_from_invite_token"
            "?token=invite123&user=alice&passHash=hash123"
        )
    assert response.status_code == 200
    mock_create.assert_called_once_with("invite123", "alice", "hash123")


@mock.patch("app.user.create_user_with_token")
def test_create_user_invalid_token(mock_create):
    mock_create.return_value = ("invalid invite token", 400)
    app.app.config["TESTING"] = True
    with app.app.test_client() as c:
        response = c.get(
            "/api/create_user_from_invite_token"
            "?token=bad&user=alice&passHash=hash123"
        )
    assert response.status_code == 400


def test_get_groups_no_token(client):
    response = client.get("/api/get_groups")
    assert response.status_code == 400


@mock.patch("app.groups.get_groups")
def test_get_groups_valid(mock_get_groups):
    mock_get_groups.return_value = [{"g_id": 1, "g_name": "alpha"}]
    app.app.config["TESTING"] = True
    with app.app.test_client() as c:
        response = c.get("/api/get_groups?token=valid")
    assert response.status_code == 200
    mock_get_groups.assert_called_once_with("valid")


def test_create_group_missing_params(client):
    response = client.get("/api/create_group?token=valid")
    assert response.status_code == 400


@mock.patch("app.groups.create_group")
def test_create_group_valid_params(mock_create_group):
    mock_create_group.return_value = 42
    app.app.config["TESTING"] = True
    with app.app.test_client() as c:
        response = c.get("/api/create_group?token=valid&name=newgroup")
    assert response.status_code == 200
    mock_create_group.assert_called_once_with("valid", "newgroup")


def test_delete_group_missing_params(client):
    response = client.get("/api/delete_group?token=valid")
    assert response.status_code == 400


def test_delete_group_invalid_id(client):
    response = client.get("/api/delete_group?token=valid&groupId=abc")
    assert response.status_code == 400


@mock.patch("app.groups.delete_group")
def test_delete_group_valid_params(mock_delete_group):
    mock_delete_group.return_value = True
    app.app.config["TESTING"] = True
    with app.app.test_client() as c:
        response = c.get("/api/delete_group?token=valid&groupId=42")
    assert response.status_code == 200
    mock_delete_group.assert_called_once_with("valid", 42)


@mock.patch("app.groups.delete_group")
def test_delete_group_not_member(mock_delete_group):
    mock_delete_group.return_value = False
    app.app.config["TESTING"] = True
    with app.app.test_client() as c:
        response = c.get("/api/delete_group?token=valid&groupId=42")
    assert response.status_code == 403


@mock.patch("app.auth.check_auth")
def test_add_user_to_group_missing_params(mock_check_auth, client):
    mock_check_auth.return_value = 42
    response = client.get("/api/add_user_to_group?token=valid&userId=1")
    assert response.status_code == 400


@mock.patch("app.auth.check_auth")
def test_add_user_to_group_invalid_token(mock_check_auth, client):
    mock_check_auth.return_value = -1
    response = client.get(
        "/api/add_user_to_group?token=bad&userId=1&groupId=2"
    )
    assert response.status_code == 400


@mock.patch("app.auth.check_auth")
def test_add_user_to_group_invalid_id(mock_check_auth, client):
    mock_check_auth.return_value = 42
    response = client.get(
        "/api/add_user_to_group?token=valid&userId=abc&groupId=2"
    )
    assert response.status_code == 400


@mock.patch("app.groups.add_user_to_group")
@mock.patch("app.auth.check_auth")
def test_add_user_to_group_valid_params(mock_check_auth, mock_add):
    mock_check_auth.return_value = 42
    mock_add.return_value = 10
    app.app.config["TESTING"] = True
    with app.app.test_client() as c:
        response = c.get(
            "/api/add_user_to_group?token=valid&userId=5&groupId=7"
        )
    assert response.status_code == 200
    mock_add.assert_called_once_with("valid", 5, 7)


@mock.patch("app.groups.add_user_to_group")
@mock.patch("app.auth.check_auth")
def test_add_user_to_group_caller_not_in_group(mock_check_auth, mock_add):
    mock_check_auth.return_value = 42
    mock_add.return_value = -1
    app.app.config["TESTING"] = True
    with app.app.test_client() as c:
        response = c.get(
            "/api/add_user_to_group?token=valid&userId=5&groupId=7"
        )
    assert response.status_code == 403


@mock.patch("app.groups.add_user_to_group")
@mock.patch("app.auth.check_auth")
def test_add_user_to_group_already_member(mock_check_auth, mock_add):
    mock_check_auth.return_value = 42
    mock_add.return_value = -2
    app.app.config["TESTING"] = True
    with app.app.test_client() as c:
        response = c.get(
            "/api/add_user_to_group?token=valid&userId=5&groupId=7"
        )
    assert response.status_code == 400


def test_remove_user_from_group_missing_params(client):
    response = client.get("/api/remove_user_from_group?userId=5")
    assert response.status_code == 400


@mock.patch("app.auth.check_auth")
def test_remove_user_from_group_invalid_token(mock_check_auth, client):
    mock_check_auth.return_value = -1
    response = client.get(
        "/api/remove_user_from_group?token=bad&userId=5&groupId=7"
    )
    assert response.status_code == 400


@mock.patch("app.auth.check_auth")
def test_remove_user_from_group_invalid_id(mock_check_auth, client):
    mock_check_auth.return_value = 42
    response = client.get(
        "/api/remove_user_from_group?token=valid&userId=abc&groupId=2"
    )
    assert response.status_code == 400


@mock.patch("app.groups.remove_user_from_group")
@mock.patch("app.auth.check_auth")
def test_remove_user_from_group_valid_params(mock_check_auth, mock_remove):
    mock_check_auth.return_value = 42
    mock_remove.return_value = 1
    app.app.config["TESTING"] = True
    with app.app.test_client() as c:
        response = c.get(
            "/api/remove_user_from_group?token=valid&userId=5&groupId=7"
        )
    assert response.status_code == 200
    mock_remove.assert_called_once_with("valid", 5, 7)


@mock.patch("app.groups.remove_user_from_group")
@mock.patch("app.auth.check_auth")
def test_remove_user_from_group_caller_not_in_group(mock_check_auth, mock_remove):
    mock_check_auth.return_value = 42
    mock_remove.return_value = -1
    app.app.config["TESTING"] = True
    with app.app.test_client() as c:
        response = c.get(
            "/api/remove_user_from_group?token=valid&userId=5&groupId=7"
        )
    assert response.status_code == 403


@mock.patch("app.groups.remove_user_from_group")
@mock.patch("app.auth.check_auth")
def test_remove_user_from_group_target_not_in_group(mock_check_auth, mock_remove):
    mock_check_auth.return_value = 42
    mock_remove.return_value = -2
    app.app.config["TESTING"] = True
    with app.app.test_client() as c:
        response = c.get(
            "/api/remove_user_from_group?token=valid&userId=5&groupId=7"
        )
    assert response.status_code == 400
