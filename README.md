# aiohttp-valera-validator

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

Fore more information read [Valera Docs](https://github.com/tsv1/valera)
