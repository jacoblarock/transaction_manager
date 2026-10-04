from unittest import mock

import utils.rate_limit as rl


def test_check_rate_limit_allows_up_to_limit():
    rl.reset_rate_limits()
    results = [rl.check_rate_limit("key1") for _ in range(rl.REQUESTS_PER_WINDOW)]
    assert results == [True] * rl.REQUESTS_PER_WINDOW


def test_check_rate_limit_blocks_over_limit():
    rl.reset_rate_limits()
    for _ in range(rl.REQUESTS_PER_WINDOW):
        rl.check_rate_limit("key1")
    assert rl.check_rate_limit("key1") is False
    assert rl.check_rate_limit("key1") is False


def test_check_rate_limit_keys_are_independent():
    rl.reset_rate_limits()
    for _ in range(rl.REQUESTS_PER_WINDOW):
        rl.check_rate_limit("key1")
    assert rl.check_rate_limit("key2") is True


def test_check_rate_limit_window_expiry():
    rl.reset_rate_limits()
    with mock.patch("utils.rate_limit.monotonic", side_effect=[100.0] * rl.REQUESTS_PER_WINDOW + [100.0]):
        for _ in range(rl.REQUESTS_PER_WINDOW):
            assert rl.check_rate_limit("key1") is True
    with mock.patch("utils.rate_limit.monotonic", return_value=100.0 + rl.WINDOW_SECONDS + 1):
        assert rl.check_rate_limit("key1") is True


def test_check_rate_limit_partial_expiry():
    rl.reset_rate_limits()
    with mock.patch("utils.rate_limit.monotonic", side_effect=[100.0] * 3 + [110.0] * 2):
        for _ in range(rl.REQUESTS_PER_WINDOW):
            rl.check_rate_limit("key1")
    with mock.patch("utils.rate_limit.monotonic", return_value=100.0 + rl.WINDOW_SECONDS + 1):
        assert rl.check_rate_limit("key1") is True
        assert rl.check_rate_limit("key1") is True
        assert rl.check_rate_limit("key1") is True
        assert rl.check_rate_limit("key1") is False


def test_reset_rate_limits_clears_state():
    rl.reset_rate_limits()
    for _ in range(rl.REQUESTS_PER_WINDOW):
        rl.check_rate_limit("key1")
    rl.reset_rate_limits()
    assert rl.check_rate_limit("key1") is True
