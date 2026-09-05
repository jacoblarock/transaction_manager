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
    assert response.data == b"healthcheck"


def test_authenticate_missing_user(client):
    response = client.get("/api/authenticate?passHash=abc123")
    assert response.status_code == 400
    assert response.data == b"invalid request format"


def test_authenticate_missing_passhash(client):
    response = client.get("/api/authenticate?user=alice")
    assert response.status_code == 400
    assert response.data == b"invalid request format"


def test_authenticate_missing_all_params(client):
    response = client.get("/api/authenticate")
    assert response.status_code == 400
    assert response.data == b"invalid request format"


@mock.patch("app.auth.authenticate")
def test_authenticate_valid_params(mock_authenticate):
    mock_authenticate.return_value = ("session_token_123", 200)
    app.app.config["TESTING"] = True
    with app.app.test_client() as c:
        response = c.get("/api/authenticate?user=alice&passHash=abc123")
    assert response.status_code == 200
    assert response.data == b"session_token_123"
    mock_authenticate.assert_called_once_with("alice", "abc123")


@mock.patch("app.auth.authenticate")
def test_authenticate_returns_error(mock_authenticate):
    mock_authenticate.return_value = ("password does not match", 400)
    app.app.config["TESTING"] = True
    with app.app.test_client() as c:
        response = c.get("/api/authenticate?user=alice&passHash=wrong")
    assert response.status_code == 400
    assert response.data == b"password does not match"


def test_auth_check_no_token(client):
    response = client.get("/api/auth_check")
    assert response.status_code == 400
    assert response.data == b"no token provided"


@mock.patch("app.auth.check_auth")
def test_auth_check_valid_session(mock_check_auth):
    mock_check_auth.return_value = 42
    app.app.config["TESTING"] = True
    with app.app.test_client() as c:
        response = c.get("/api/auth_check?token=valid_token")
    assert response.status_code == 200
    assert response.data == b"success"
    mock_check_auth.assert_called_once_with("valid_token")


@mock.patch("app.auth.check_auth")
def test_auth_check_session_not_found(mock_check_auth):
    mock_check_auth.return_value = -1
    app.app.config["TESTING"] = True
    with app.app.test_client() as c:
        response = c.get("/api/auth_check?token=invalid_token")
    assert response.status_code == 400
    assert response.data == b"session not found"


def test_create_user_missing_params(client):
    response = client.get("/api/create_user_from_invite_token")
    assert response.status_code == 400
    assert response.data == b"invalid request format"


def test_create_user_partial_params(client):
    response = client.get("/api/create_user_from_invite_token?token=abc&user=alice")
    assert response.status_code == 400
    assert response.data == b"invalid request format"


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
    assert response.data == b"success"
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
    assert response.data == b"invalid invite token"
