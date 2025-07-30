import json
import httpx
import pytest


def echo(request):
    response = httpx.Response(200, content=httpx.JSON({
        'method': request.method,
        'query-params': dict(request.url.params.items()),
        'content-type': request.headers.get('Content-Type'),
        'json': request.json(),
    }))
    return response


@pytest.fixture
def server():
    with httpx.serve_http(echo) as server:
        yield server


def test_get(server):
    r = httpx.get(server.url)
    assert r.status_code == 200
    assert r.json() == {
        'method': 'GET',
        'query-params': {},
        'content-type': None,
        'json': None,
    }


def test_post(server):
    data = httpx.JSON({"data": 123})
    r = httpx.post(server.url, content=data)
    assert r.status_code == 200
    assert r.json() == {
        'method': 'POST',
        'query-params': {},
        'content-type': 'application/json',
        'json': {"data": 123},
    }


def test_put(server):
    data = httpx.JSON({"data": 123})
    r = httpx.put(server.url, content=data)
    assert r.status_code == 200
    assert r.json() == {
        'method': 'PUT',
        'query-params': {},
        'content-type': 'application/json',
        'json': {"data": 123},
    }


def test_patch(server):
    data = httpx.JSON({"data": 123})
    r = httpx.patch(server.url, content=data)
    assert r.status_code == 200
    assert r.json() == {
        'method': 'PATCH',
        'query-params': {},
        'content-type': 'application/json',
        'json': {"data": 123},
    }


def test_delete(server):
    r = httpx.delete(server.url)
    assert r.status_code == 200
    assert r.json() == {
        'method': 'DELETE',
        'query-params': {},
        'content-type': None,
        'json': None,
    }
