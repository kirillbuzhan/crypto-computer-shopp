"""Страницы сайта, API лаборатории и работа за прокси с префиксом адреса."""

import pytest
from fastapi.testclient import TestClient

import config
from content.topics import LAB_THEORY, TOPICS, TOPICS_BY_SLUG
from main import app

client = TestClient(app)
HTML = {"accept": "text/html"}


@pytest.mark.parametrize("path", ["/", "/lab", "/theory", "/reference", "/about"] + [f"/theory/{t.slug}" for t in TOPICS])
def test_pages_render(path):
    response = client.get(path, headers=HTML)
    assert response.status_code == 200
    assert "<title>" in response.text
    assert response.headers["x-content-type-options"] == "nosniff"


def test_every_theory_link_points_to_existing_topic():
    for slugs in LAB_THEORY.values():
        for slug in slugs:
            assert slug in TOPICS_BY_SLUG


def test_lab_preselects_algorithm():
    assert 'data-initial-algorithm="hamming"' in client.get("/lab?algorithm=hamming").text
    assert 'data-initial-algorithm=""' in client.get("/lab?algorithm=<script>").text


def test_not_found():
    assert client.get("/theory/unknown", headers=HTML).status_code == 404
    assert client.get("/nothing-here", headers=HTML).status_code == 404


def test_healthz():
    assert client.get("/healthz").text == "ok"


def test_transmit_validates_input():
    assert client.post("/transmit", json={"algorithm": "huffman", "message": "x" * (config.MAX_MESSAGE_LENGTH + 1)}).status_code == 400
    assert client.post("/transmit", json={"algorithm": "unknown", "message": "x"}).status_code == 400
    assert client.post("/transmit", json={"algorithm": "huffman"}).status_code == 400
    assert client.post("/transmit", json={"algorithm": "huffman", "message": "абракадабра"}).status_code == 200


def test_elgamal_flow_is_stateless():
    keys = client.post("/elgamal/keys", json={"bits": 96}).json()
    assert isinstance(keys["p"], str)  # большие числа — строками, чтобы JS не терял цифры
    body = {"algorithm": "elgamal", "message": "Тест", "keys": {name: keys[name] for name in ("p", "g", "x", "certificate")}}
    response = client.post("/transmit", json=body)
    assert response.status_code == 200
    assert response.json()["decoded"] == "Тест"

    del body["keys"]["certificate"]
    assert client.post("/transmit", json=body).status_code == 400


def test_root_path_prefixes_links():
    prefixed = TestClient(app, root_path="/crypto-lab")
    page = prefixed.get("/theory/huffman", headers=HTML).text
    assert 'href="/crypto-lab/static/site.css' in page
    assert 'data-root="/crypto-lab"' in page
    assert 'href="/crypto-lab/lab?algorithm=huffman"' in page


@pytest.mark.parametrize("prefix_in_path", [True, False])
def test_root_path_with_and_without_prefix_stripping(monkeypatch, prefix_in_path):
    """ROOT_PATH задан, а прокси либо передаёт /crypto-lab/... целиком, либо отрезает префикс."""
    monkeypatch.setattr(app, "root_path", "/crypto-lab")
    prefix = "/crypto-lab" if prefix_in_path else ""
    proxied = TestClient(app)
    page = proxied.get(f"{prefix}/theory/hamming", headers=HTML)
    assert page.status_code == 200
    assert 'href="/crypto-lab/static/site.css' in page.text
    assert proxied.get(f"{prefix}/static/site.css").status_code == 200
    assert proxied.post(f"{prefix}/transmit", json={"algorithm": "reverse", "message": "abc"}).json()["encoded"] == "cba"
