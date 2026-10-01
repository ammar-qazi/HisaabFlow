"""
The backend serves the built React app next to the API.
"""
import pytest
from fastapi import APIRouter, FastAPI
from fastapi.testclient import TestClient

from backend.api.frontend import register_frontend


@pytest.fixture
def client(tmp_path):
    build = tmp_path / "build"
    (build / "static" / "js").mkdir(parents=True)
    (build / "index.html").write_text("<html>app</html>")
    (build / "static" / "js" / "main.js").write_text("console.log(1)")
    (tmp_path / "secret.txt").write_text("outside the build dir")

    app = FastAPI()
    api = APIRouter()

    @api.get("/configs")
    async def configs():
        return {"configurations": []}

    app.include_router(api, prefix="/api/v1")
    register_frontend(app, build)
    return TestClient(app)


def test_root_serves_index(client):
    response = client.get("/")
    assert response.status_code == 200 and response.text == "<html>app</html>"


def test_static_file(client):
    assert client.get("/static/js/main.js").text == "console.log(1)"


def test_client_route_falls_back_to_index(client):
    assert client.get("/transactions/2025").text == "<html>app</html>"


def test_api_still_json(client):
    assert client.get("/api/v1/configs").json() == {"configurations": []}


def test_unknown_api_path_is_404_not_index(client):
    response = client.get("/api/v1/does-not-exist")
    assert response.status_code == 404
    assert "app" not in response.text


def test_no_files_outside_build_dir(client):
    response = client.get("/..%2Fsecret.txt")
    assert "outside the build dir" not in response.text
