"""
Unit tests for the generic Google Sheets batch_update_spreadsheet tool and its
request validation helper.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from core.utils import UserInputError
from gsheets.sheets_helpers import (
    MAX_BATCH_UPDATE_REPLY_CHARS,
    MAX_BATCH_UPDATE_REQUESTS,
    _validate_batch_update_requests,
)


def _unwrap(fn):
    """Unwrap decorated function to access the underlying coroutine."""
    while hasattr(fn, "__wrapped__"):
        fn = fn.__wrapped__
    return fn


def test_limits_match_the_spec():
    assert MAX_BATCH_UPDATE_REQUESTS == 100
    assert MAX_BATCH_UPDATE_REPLY_CHARS == 4000


def test_validate_returns_kinds_in_order():
    kinds = _validate_batch_update_requests([{"setBasicFilter": {}}, {"sortRange": {}}])
    assert kinds == ["setBasicFilter", "sortRange"]


def test_validate_rejects_empty():
    with pytest.raises(UserInputError, match="at least one request"):
        _validate_batch_update_requests([])


def test_validate_rejects_over_limit():
    with pytest.raises(UserInputError, match="100"):
        _validate_batch_update_requests([{"sortRange": {}}] * 101)
    assert len(_validate_batch_update_requests([{"sortRange": {}}] * 100)) == 100


def test_validate_rejects_non_dict_item():
    with pytest.raises(UserInputError, match=r"requests\[1\]"):
        _validate_batch_update_requests([{"sortRange": {}}, "x"])


@pytest.mark.parametrize(
    "requests",
    [[{"sortRange": {}, "addChart": {}}], [{}]],
)
def test_validate_rejects_multi_key_item(requests):
    with pytest.raises(UserInputError) as exc_info:
        _validate_batch_update_requests(requests)
    message = str(exc_info.value)
    assert "requests[0]" in message
    assert "exactly one request type" in message
