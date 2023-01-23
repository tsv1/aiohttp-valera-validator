from functools import wraps
from http import HTTPStatus
from typing import Any, Callable, Coroutine, List, Optional

import valera
from aiohttp.web import Request, Response, json_response
from district42.types import GenericSchema

__all__ = ("validate", "HandlerType",)

HandlerType = Callable[..., Coroutine[Any, Any, Response]]


class validate:
    def __init__(self, *, segments: Optional[GenericSchema] = None,
                 params: Optional[GenericSchema] = None,
                 headers: Optional[GenericSchema] = None,
                 json: Optional[GenericSchema] = None) -> None:
        if (segments is None) and (params is None) and (headers is None) and (json is None):
            raise ValueError("At least one argument must be provided")
        self._segments = segments
        self._params = params
        self._headers = headers
        self._json = json

    def _validate(self, value: Any, schema: GenericSchema) -> List[str]:
        result = valera.validate(schema, value)
        formatter = valera.Formatter()
        errors = [e.format(formatter) for e in result.get_errors()]
        return errors

    async def _validate_request(self, request: Request) -> List[str]:
        errors = []
        if self._segments:
            errors += self._validate(request.match_info, self._segments)
        if self._params:
            # fix: params could have multiple values for the same key
            errors += self._validate(dict(request.query), self._params)
        if self._headers:
            # fix: headers could have multiple values for the same key
            errors += self._validate(dict(request.headers), self._headers)
        if self._json:
            try:
                payload = await request.json()
            except BaseException as e:
                errors += [repr(e)]
            else:
                errors += self._validate(payload, self._json)
        return errors

    def create_error_response(self, request: Request, errors: List[str]) -> Response:
        return json_response({"errors": errors}, status=HTTPStatus.BAD_REQUEST)

    def __call__(self, fn: HandlerType) -> HandlerType:
        @wraps(fn)
        async def wrapped(request: Request) -> Response:
            errors = await self._validate_request(request)
            if len(errors) > 0:
                return self.create_error_response(request, errors)
            return await fn(request)
        return wrapped
