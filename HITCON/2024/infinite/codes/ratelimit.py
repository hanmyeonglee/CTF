from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.routing import Match, Mount
from limits import parse
from limits.storage import storage_from_string
from limits.aio.strategies import FixedWindowRateLimiter

from .config import config

redis = storage_from_string(config['rate_limit']['redis_uri'])
moving_window = FixedWindowRateLimiter(redis)


# create a fastapi middleware
class RateLimitMiddleware(BaseHTTPMiddleware):
    __limits = {}
    default_limit = parse(config['rate_limit']['default'])

    @staticmethod
    def handler_name(handler):
        return f'{handler.__module__}.{handler.__name__}'

    @classmethod
    def limit(cls, limit):
        def decorator(handler):
            cls.__limits[cls.handler_name(handler)] = parse(limit)
            return handler
        return decorator

    async def dispatch(self, request, call_next):
        if not config['rate_limit']['enabled']:
            return await call_next(request)

        app = request.app
        for route in app.routes:
            if isinstance(route, Mount):
                continue

            match_, _ = route.matches(request.scope)
            if match_ == Match.FULL:
                handler = route.endpoint
                break
        else:
            return await call_next(request)

        name = self.handler_name(handler)
        limit = self.__limits.get(name, self.default_limit)

        # use http path, method, and client ip as key
        key = (request.url.path, request.method, request.client.host)

        success = await moving_window.hit(limit, *key)
        if not success:
            return JSONResponse({'error': 'rate limit exceeded'}, status_code=429)

        return await call_next(request)

