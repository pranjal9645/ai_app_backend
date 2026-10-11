
from unittest.mock import Mock, patch

import pytest
from fastapi import Request
from redis.exceptions import RedisError

from app.core.rate_limit import rate_limit , rate_limit_by_user
from types import SimpleNamespace
from app.core.exceptions import RateLimitExceededError , RateLimitServiceUnavailableError


def make_request(path: str) -> Request:
    route_path = (
        "/conversations/{conversation_id}/messages"
        if path.startswith("/conversations/")
        else path
    )

    scope = {
        "type": "http",
        "method": "POST",
        "path": path,
        "headers": [],
        "query_string": b"",
        "server": ("testserver", 80),
        "client": ("127.0.0.1", 12345),
        "scheme": "http",
        "root_path": "",
        "app": None,
        "router": None,
        "endpoint": None,
        "path_params": {},
        "route": Mock(path=route_path),
    }

    return Request(scope)


def test_rate_limit_allows_requests_within_limit():
    request = make_request("/conversations/101/messages")

    with patch("app.core.rate_limit.redis_client") as redis_mock:
        redis_mock.eval.return_value = [1, 60]

        dependency = rate_limit(max_requests=10, window_seconds=60)

        # No exception means the request is allowed.
        assert dependency(request) is None


def test_rate_limit_rejects_requests_over_limit():
    request = make_request("/conversations/101/messages")

    with patch("app.core.rate_limit.redis_client") as redis_mock:
        redis_mock.eval.return_value = [11, 42]

        dependency = rate_limit(
            max_requests=10,
            window_seconds=60,
        )

        with pytest.raises(RateLimitExceededError) as exc_info:
            dependency(request)

        assert exc_info.value.retry_after == 42
        assert exc_info.value.code == "RATE_LIMIT_EXCEEDED"

def test_different_conversation_ids_share_route_key():
    request_one = make_request("/conversations/101/messages")
    request_two = make_request("/conversations/202/messages")

    with patch("app.core.rate_limit.redis_client") as redis_mock:
        redis_mock.eval.return_value = [1, 60]

        dependency = rate_limit(max_requests=10, window_seconds=60)

        dependency(request_one)
        dependency(request_two)

        keys = [
            call.args[2]
            for call in redis_mock.eval.call_args_list
        ]

        assert keys[0] == keys[1]


def test_rate_limit_returns_503_when_redis_fails():
    request = make_request("/conversations/101/messages")

    with patch("app.core.rate_limit.redis_client") as redis_mock:
        redis_mock.eval.side_effect = RedisError(
            "Redis unavailable"
        )

        dependency = rate_limit(
            max_requests=10,
            window_seconds=60,
        )

        with pytest.raises(
            RateLimitServiceUnavailableError
        ) as exc_info:
            dependency(request)

        assert (
            exc_info.value.code
            == "RATE_LIMIT_SERVICE_UNAVAILABLE"
        )



def test_user_rate_limit_uses_user_id():
    request = make_request("/assistant/chat")
    user = SimpleNamespace(id="user-123")

    with patch("app.core.rate_limit.redis_client") as redis_mock:
        redis_mock.eval.return_value = [1, 60]

        dependency = rate_limit_by_user(10, 60)
        dependency(request, current_user=user)

        key = redis_mock.eval.call_args.args[2]
        print("ACTUAL KEY:", repr(key))
        assert key == "rate_limit:/assistant/chat:user:user-123"

def test_different_users_get_different_rate_limit_keys():
    request = make_request("/assistant/chat")

    with patch("app.core.rate_limit.redis_client") as redis_mock:
        redis_mock.eval.return_value = [1, 60]

        dependency = rate_limit_by_user(10, 60)

        dependency(
            request,
            current_user=SimpleNamespace(id="user-123"),
        )
        dependency(
            request,
            current_user=SimpleNamespace(id="user-456"),
        )

        keys = [
            call.args[2]
            for call in redis_mock.eval.call_args_list
        ]

        assert keys[0] != keys[1]
        assert "user:user-123" in keys[0]
        assert "user:user-456" in keys[1]


def test_same_user_shares_limit_across_ip_addresses():
    request_one = make_request("/assistant/chat")
    request_two = make_request("/assistant/chat")

    request_two.scope["client"] = ("192.0.2.10", 12345)

    user = SimpleNamespace(id="user-123")

    with patch("app.core.rate_limit.redis_client") as redis_mock:
        redis_mock.eval.return_value = [1, 60]

        dependency = rate_limit_by_user(10, 60)

        dependency(request_one, current_user=user)
        dependency(request_two, current_user=user)

        keys = [
            call.args[2]
            for call in redis_mock.eval.call_args_list
        ]

        assert keys[0] == keys[1]

