# aiohttp-valera-validator

[![Codecov](https://img.shields.io/codecov/c/github/tsv1/aiohttp-valera-validator/master.svg?style=flat-square)](https://codecov.io/gh/tsv1/aiohttp-valera-validator)
[![PyPI](https://img.shields.io/pypi/v/aiohttp-valera-validator.svg?style=flat-square)](https://pypi.python.org/pypi/aiohttp-valera-validator/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/aiohttp-valera-validator?style=flat-square)](https://pypi.python.org/pypi/aiohttp-valera-validator/)
[![Python Version](https://img.shields.io/pypi/pyversions/aiohttp-valera-validator.svg?style=flat-square)](https://pypi.python.org/pypi/aiohttp-valera-validator/)

Request validation for [aiohttp](https://docs.aiohttp.org/en/stable/) (via [valera](https://github.com/tsv1/valera))

## Installation

```shell
$ pip3 install aiohttp-valera-validator
```

## Usage

```python
from aiohttp.web import Application, json_response, route, run_app
from district42 import schema
from aiohttp_valera_validator import validate

ParamsSchema = schema.dict({
    "q": schema.str.len(1, ...)
})

@validate(params=ParamsSchema)
async def handler(request):
    q = request.query["q"]
    return json_response({"q": q})


app = Application()
app.add_routes([route("GET", "/users", handler)])
run_app(app)
```

```javascript
// http /users?q=Bob
{
    "q": "Bob"
}
```

```javascript
// http /users
{
    "errors": [
        "Value <class 'str'> at _['q'] must have at least 1 element, but it has 0 elements"
    ]
}
```

## Docs

### Query params validation

```python
from district42 import schema
from aiohttp_valera_validator import validate

# schema.dict is strict by default (all keys must be present)
ParamsSchema = schema.dict({
    "q": schema.str.len(1, ...)
})

@routes.get("/users")
@validate(params=ParamsSchema)
async def handler(request):
    q = request.query["q"]
    return json_response({"q": q})
```

### Headers validation

```python
from district42 import schema
from aiohttp_valera_validator import validate
from multidict import istr

# "..." means that there can be any other keys
# headers are case-insensitive, so we use istr for
HeadersSchema = schema.dict({
    istr("User-Agent"): schema.str.len(1, ...),
    ...: ...
})

@routes.get("/users")
@validate(headers=HeadersSchema)
async def handler(request):
    user_agent = request.headers["User-Agent"]
    return json_response({"user_agent": user_agent})
```

### JSON body validation

```python
from district42 import schema
from aiohttp_valera_validator import validate

BodySchema = schema.dict({
    "id": schema.int.min(1),
    "name": schema.str.len(1, ...),
})

@routes.post("/users")
@validate(json=BodySchema)
async def handler(request):
    payload = await request.json()
    return json_response({
        "id": payload["id"],
        "name": payload["name"]
    })
```

### URL segments validation

Segments — is a variable part of URL path (aiohttp [uses](https://docs.aiohttp.org/en/stable/web_quickstart.html#variable-resources) `match_info` for it)

```python
from district42 import schema
from aiohttp_valera_validator import validate

SegmentsSchema = schema.dict({
    "user_id": schema.str.regex(r"[1-9][0-9]*"),
})

@routes.get("/users/{user_id}")
@validate(segments=SegmentsSchema)
async def handler(request):
    user_id = int(request.match_info["user_id"])
    return json_response({"user_id": user_id})
```

### Custom response

```python
from http import HTTPStatus
from aiohttp.web import Request, Response
from aiohttp_valera_validator import validate as validate_orig

class validate(validate_orig):
    def create_error_response(self, request: Request, errors: List[str]) -> Response:
        status = HTTPStatus.UNPROCESSABLE_ENTITY
        body = "<ul>" + "".join(f"<li>{error}</li>" for error in errors) + "</ul>"
        return Response(status=status, text=body, headers={"Content-Type": "text/html"})
```

—

Fore more information read [valera docs](https://github.com/tsv1/valera)
