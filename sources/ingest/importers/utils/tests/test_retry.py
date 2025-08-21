from unittest.mock import patch

import pytest

from ingest.importers.utils.retry import retry_twice_5s_intervals


def test_retry_twice_5s_intervals_failure():
    """
    Test retry_twice_5s_intervals raises an exception after two retries
    """
    with patch("ingest.importers.utils.retry.time.sleep") as mock_sleep:
        with pytest.raises(ZeroDivisionError):
            retry_twice_5s_intervals(lambda: 1 / 0)  # ZeroDivisionError
        assert mock_sleep.call_count == 2
        # Check all calls' *args & **kwargs
        assert mock_sleep.call_args_list[0] == ((5,), {})
        assert mock_sleep.call_args_list[1] == ((5,), {})


def test_retry_twice_5s_intervals_first_succeed():
    """
    Test retry_twice_5s_intervals returns result of callable on success
    """
    with patch("ingest.importers.utils.retry.time.sleep") as mock_sleep:
        result = retry_twice_5s_intervals(lambda: 42)
        assert result == 42
        assert mock_sleep.call_count == 0


def test_retry_twice_5s_intervals_passes_args_and_kwargs():
    """
    Test retry_twice_5s_intervals passes args and kwargs to the callable
    """
    with patch("ingest.importers.utils.retry.time.sleep") as mock_sleep:
        result = retry_twice_5s_intervals(
            lambda *args, **kwargs: sum(args) + sum(kwargs.values()), 1, 2, y=3, z=4
        )
        assert result == 10
        assert mock_sleep.call_count == 0


def test_retry_twice_5s_intervals_first_fail_then_succeed():
    """
    Test retry_twice_5s_intervals retries the callable that fails once
    """
    try_count = 0

    def callable_that_fails_and_then_succeeds():
        nonlocal try_count
        try_count += 1
        if try_count == 2:
            return 123
        raise RuntimeError

    with patch("ingest.importers.utils.retry.time.sleep") as mock_sleep:
        result = retry_twice_5s_intervals(callable_that_fails_and_then_succeeds)
        assert result == 123
        assert try_count == 2
        assert mock_sleep.call_count == 1
        # Check all calls' *args & **kwargs
        assert mock_sleep.call_args_list[0] == ((5,), {})
