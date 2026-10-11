from fastapi import Request , Depends
from redis.exceptions import RedisError
from app.models.user import User
from app.core.security import get_current_user
from app.core.exceptions import RateLimitExceededError , RateLimitServiceUnavailableError


from app.db.redis import redis_client

RATE_LIMIT_SCRIPT = """
local count = redis.call("INCR", KEYS[1])

if count == 1 then
    redis.call("EXPIRE", KEYS[1], ARGV[1])
end

local ttl = redis.call("TTL", KEYS[1])

return {count, ttl}
"""

def rate_limit(max_requests : int , window_seconds : int):

    """Limit requests by client IP."""

    def dependency(request : Request) -> None:
        
        client_ip = (
            request.client.host
            if request.client
            else "unknown"
        )

        _check_rate_limit(request=request , identity=f"ip:{client_ip}" , max_requests=max_requests, window_seconds=window_seconds)

    return dependency


def rate_limit_by_user(max_requests : int , window_seconds : int):
      """Limit authenticated requests by user ID."""

      def dependency( request: Request, current_user: User = Depends(get_current_user)) -> None:

          _check_rate_limit(request=request , identity=f"user:{current_user.id}" , max_requests=max_requests , window_seconds=window_seconds)


      return dependency



def _check_rate_limit(request : Request , identity : str , max_requests : int , window_seconds : int) -> None:

    route = request.scope.get("route")

    route_name = route.path if route is not None else request.url.path

    key = f"rate_limit:{route_name}:{identity}"

    try:
        result = redis_client.eval(RATE_LIMIT_SCRIPT , 1 , key , window_seconds)

    except RedisError :

        raise RateLimitServiceUnavailableError()
    count , ttl  = result

    if count > max_requests :
        raise RateLimitExceededError(ttl)

