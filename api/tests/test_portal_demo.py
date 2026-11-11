import os
import tempfile

TMP = tempfile.mkdtemp()
os.environ.setdefault("DATABASE_URL", f"sqlite:///{TMP}/teste.db")
os.environ.setdefault("UPLOAD_DIR", f"{TMP}/uploads")

import re  # noqa: E402

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402

PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 50


@pytest.fixture
def c(monkeypatch):
    monkeypatch.setenv("PORTAL_DEMO_USUARIO", "robo-teste")
    monkeypatch.setenv("PORTAL_DEMO_SENHA", "senha-teste")
    with TestClient(app) as cliente:
        yield cliente


def entrar(c, senha="senha-teste"):
    return c.post("/portal-demo/login", data={"usuario": "robo-teste", "senha": senha}, follow_redirects=False)


def test_desativado_sem_credenciais(monkeypatch):
    monkeypatch.delenv("PORTAL_DEMO_USUARIO", raising=False)
    monkeypatch.delenv("PORTAL_DEMO_SENHA", raising=False)
    with TestClient(app) as c:
        assert c.get("/portal-demo/").status_code == 503
        assert entrar(c).status_code == 503


def test_exige_login(c):
    assert 'id="usuario"' in c.get("/portal-demo/").text
    r = c.get("/portal-demo/nova", follow_redirects=False)
    assert r.status_code == 303 and r.headers["location"] == "/portal-demo/"
    assert c.post("/portal-demo/ordens", data={"endereco": "Rua A", "tipo": "outros"}, follow_redirects=False).status_code == 303


def test_senha_errada(c):
    r = entrar(c, senha="errada")
    assert r.status_code == 401 and "inválidos" in r.text
    assert "portal_sessao" not in r.cookies


def test_fluxo_do_robo(c):
    r = entrar(c)
    assert r.status_code == 303
    assert "httponly" in r.headers["set-cookie"].lower()
    assert 'id="endereco"' in c.get("/portal-demo/nova").text

    r = c.post(
        "/portal-demo/ordens",
        data={"endereco": "Rua das Acácias, 120", "tipo": "buraco_pavimento",
              "descricao": "Relato Zela nº 7: buraco", "referencia": "7"},
        files={"anexo": ("f.png", PNG, "image/png")},
    )
    assert r.status_code == 200
    numero = re.search(r'id="numero-os">(OS-\d{4}-\d{6})<', r.text).group(1)
    assert "Rua das Acácias, 120" in r.text and 'id="os-referencia">7<' in r.text
    assert numero in c.get("/portal-demo/ordens").text


def test_validacoes_do_formulario(c):
    entrar(c)
    assert c.post("/portal-demo/ordens", data={"endereco": "x", "tipo": "outros"}).status_code == 422
    assert c.post("/portal-demo/ordens", data={"endereco": "Rua A, 1", "tipo": "vazamento"}).status_code == 422
    r = c.post("/portal-demo/ordens", data={"endereco": "Rua A, 1", "tipo": "outros"},
               files={"anexo": ("a.txt", b"oi", "text/plain")})
    assert r.status_code == 422


def test_html_e_escapado(c):
    entrar(c)
    r = c.post("/portal-demo/ordens", data={"endereco": "<script>alert(1)</script>", "tipo": "outros"})
    assert "<script>alert(1)</script>" not in r.text and "&lt;script&gt;" in r.text


def test_sair_encerra_sessao(c):
    entrar(c)
    c.post("/portal-demo/sair")
    assert c.get("/portal-demo/nova", follow_redirects=False).status_code == 303
