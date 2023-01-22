from pytest import raises

from aiohttp_valera_validator import validate


def test_validate():
    with raises(Exception) as exception:
        validate()

    assert exception.type is ValueError
