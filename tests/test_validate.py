import string
from http import HTTPStatus

import pytest
from district42 import schema
from multidict import istr
from pytest import raises

from aiohttp_valera_validator import validate

from ._utils import make_client, make_handler, make_server


def test_validate():
    with raises(Exception) as exception:
        validate()

    assert exception.type is ValueError


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


async def test_params():
    params_schema = schema.dict({
        "q": schema.str.len(1, ...)
    })
    validator = validate(params=params_schema)
    handler = make_handler("GET", "/users", validator)

    async with make_client(make_server(handler)) as client:
        response = await client.get("/users", params={"q": "Bob"})
        assert response.status == HTTPStatus.NO_CONTENT

        response = await client.get("/users", params={"q": ""})
        assert response.status == HTTPStatus.BAD_REQUEST
        assert await response.json() == {
            "errors": [
                "Value <class 'str'> at _['q'] must have at least 1 element, but it has 0 elements"
            ]
        }


@pytest.mark.parametrize("user_agent", ["User-Agent", "user-agent", "USER-AGENT"])
async def test_headers(user_agent: str):
    headers_schema = schema.dict({
        istr("User-Agent"): schema.str.len(1, ...),
        ...: ...
    })
    validator = validate(headers=headers_schema)
    handler = make_handler("GET", "/", validator)

    async with make_client(make_server(handler)) as client:
        response = await client.get("/", headers={user_agent: "Mozilla/5.0"})
        assert response.status == HTTPStatus.NO_CONTENT

        response = await client.get("/", headers={user_agent: ""})
        assert response.status == HTTPStatus.BAD_REQUEST
        assert await response.json() == {
            "errors": [
                "Value <class 'str'> at _['User-Agent'] must have at least 1 element, "
                "but it has 0 elements"
            ]
        }


async def test_json_body():
    user_schema = schema.dict({
        "id": schema.int.min(1),
        "name": schema.str.len(1, ...),
    })
    validator = validate(json=user_schema)
    handler = make_handler("POST", "/users", validator)

    async with make_client(make_server(handler)) as client:
        response = await client.post("/users", json={"id": 1, "name": "Bob"})
        assert response.status == HTTPStatus.NO_CONTENT

        response = await client.post("/users", json={"id": "1"})
        assert response.status == HTTPStatus.BAD_REQUEST
        assert await response.json() == {
            "errors": [
                "Value '1' at _['id'] must be <class 'int'>, but <class 'str'> given",
                "Key _['name'] does not exist",
            ]
        }

        response = await client.post("/users", data=b"][")
        assert response.status == HTTPStatus.BAD_REQUEST
        assert await response.json() == {
            "errors": [
                "JSONDecodeError('Expecting value: line 1 column 1 (char 0)')"
            ]
        }
