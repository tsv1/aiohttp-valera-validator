from http import HTTPStatus

from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer
from aiohttp.web import Application, Request, Response
from aiohttp.web_routedef import RouteDef

from aiohttp_valera_validator import validate
from aiohttp_valera_validator._validate import HandlerType

__all__ = ("make_server", "make_client", "make_handler")


def make_server(handler) -> TestServer:
    app = Application()
    app.add_routes([handler])
    return TestServer(app)


def make_client(server: TestServer) -> TestClient:
    return TestClient(server)


async def default_handler(request: Request) -> Response:
    return Response(status=HTTPStatus.NO_CONTENT)


def make_handler(method: str, route: str, validator: validate, *,
                 handler: HandlerType = default_handler) -> RouteDef:
    return web.route(method, route, validator(handler))
