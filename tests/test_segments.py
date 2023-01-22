import string
from http import HTTPStatus

from district42 import schema

from aiohttp_valera_validator import validate

from ._utils import make_client, make_handler, make_server


async def test_segments():
    segments_schema = schema.dict({
        "user_id": schema.str.alphabet(string.digits)
    })
    validator = validate(segments=segments_schema)
    handler = make_handler("GET", "/users/{user_id}", validator)

    async with make_client(make_server(handler)) as client:
        response = await client.get("/users/1")
        assert response.status == HTTPStatus.NO_CONTENT

        response = await client.get("/users/user")
        assert response.status == HTTPStatus.BAD_REQUEST
        assert await response.json() == {
            "errors": [
                "Value <class 'str'> must contain only '0123456789', but 'user' given"
            ]
        }
