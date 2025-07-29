from __future__ import annotations

import pytest
from starlette.applications import Starlette
from starlette.middleware import Middleware
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
from starlette.routing import Route
from starlette.testclient import TestClient

from unpoly.contrib.starlette import UnpolyMiddleware


@pytest.fixture
def basic_app():
    async def test_endpoint(request: Request):
        return Response("Test response")

    app = Starlette(
        routes=[Route("/test", test_endpoint)],
        middleware=[Middleware(UnpolyMiddleware)],
    )
    return app


@pytest.fixture
def redirect_app():
    async def redirect_endpoint(request: Request):
        up = request.state.up
        up.set_title("Testing")
        return RedirectResponse("/redirect?test=abc")

    app = Starlette(
        routes=[Route("/test", redirect_endpoint)],
        middleware=[Middleware(UnpolyMiddleware)],
    )
    return app


def test_starlette_middleware_headers(basic_app: Starlette):
    client = TestClient(basic_app)
    response = client.get("/test", headers={"X-Up-Version": "2.2.1"})
    assert response.headers["X-Up-Method"] == "GET"
    assert "X-Up-Location" not in response.headers

    client = TestClient(basic_app)
    response = client.get(
        "/test?p1=v1&_up_title=test", headers={"X-Up-Version": "2.2.1"}
    )
    assert response.headers["X-Up-Location"] == "/test?p1=v1"


def test_starlette_up_cookie(basic_app: Starlette):
    # Setting the cookie
    client = TestClient(basic_app)
    response = client.post("/test")
    assert "_up_method=POST" in response.headers.get("set-cookie", "")

    # Deleting the cookie if set
    assert client.cookies["_up_method"] == "POST"
    response = client.get("/test", headers={"X-Up-Version": "2.2.1"})
    set_cookie_header = response.headers.get("set-cookie", "")
    assert "_up_method=" in set_cookie_header
    assert "_up_method=POST" not in set_cookie_header

    # No cookie set for GET
    response = client.get("/test", headers={"X-Up-Version": "2.2.1"})
    assert (
        "set-cookie" not in response.headers
        or "_up_method" not in response.headers.get("set-cookie", "")
    )


def test_starlette_redirect_up_params(redirect_app: Starlette):
    client = TestClient(redirect_app)
    response = client.get(
        "/test", headers={"X-Up-Version": "2.2.1"}, follow_redirects=False
    )
    assert response.headers["Location"] == "/redirect?test=abc&_up_title=%22Testing%22"
