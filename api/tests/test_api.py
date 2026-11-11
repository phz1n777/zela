import io
import os
import tempfile

TMP = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = f"sqlite:///{TMP}/teste.db"
os.environ["UPLOAD_DIR"] = f"{TMP}/uploads"
os.environ["ROBO_TOKEN"] = "token-robo-teste"
os.environ["OPERADOR_TOKEN"] = "token-operador-teste"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from PIL import Image  # noqa: E402

from app import main  # noqa: E402
from app.main import app  # noqa: E402
from app.services import vision  # noqa: E402



def _imagem(formato, tamanho=(8, 6), **opcoes):
    saida = io.BytesIO()
    Image.new("RGB", tamanho, (200, 30, 30)).save(saida, format=formato, **opcoes)
    return saida.getvalue()


PNG = _imagem("PNG")
ROBO = {"x-robo-token": "token-robo-teste"}
OPERADOR = {"x-operador-token": "token-operador-teste"}


@pytest.fixture
def c():
    with TestClient(app) as cliente:
        yield cliente


@pytest.fixture
def com_dano(monkeypatch):
    sugestao = vision.Sugestao(label="dano_na_pista", confidence=0.81, model="best.pt")
    monkeypatch.setattr(main.vision, "sugerir", lambda _: sugestao)


def enviar(c, **extra):
    dados = {"location": "Av. Paulista, 1000 (em frente ao metrô)", "description": "buraco grande"}
    dados.update(extra)
    return c.post("/api/reports", data=dados, files={"photo": ("x.png", PNG, "image/png")})


def test_health(c):
    assert c.get("/health").json() == {"status": "ok"}


def test_sem_modelo_nao_ha_sugestao_e_categoria_e_outro(c):
    r = enviar(c)
    assert r.status_code == 201
    d = r.json()
    assert (d["status"], d["source"], d["category"]) == ("recebido", "cidadao", "outro")
    assert (d["cv_label"], d["cv_confidence"], d["cv_model"], d["cv_reviewed"]) == (None, None, None, False)
    assert d["confirm_token"]


def test_sugestao_da_visao_vira_categoria(c, com_dano):
    d = enviar(c).json()
    assert (d["category"], d["cv_label"], d["cv_confidence"]) == ("dano_na_pista", "dano_na_pista", 0.81)


def test_categoria_manual_prevalece_sobre_sugestao(c, com_dano):
    d = enviar(c, category="bueiro").json()
    assert (d["category"], d["cv_label"]) == ("bueiro", "dano_na_pista")


def test_confirmacao_exige_token_e_vale_uma_vez(c, com_dano):
    d = enviar(c).json()
    url = f"/api/reports/{d['id']}/confirmation"

    assert c.post(url, json={"category": "outro", "confirm_token": "errado"}).status_code == 403

    r = c.post(url, json={"category": "outro", "confirm_token": d["confirm_token"]})
    assert r.status_code == 200
    assert (r.json()["category"], r.json()["cv_reviewed"]) == ("outro", True)
    assert "confirm_token" not in r.json()

    assert c.post(url, json={"category": "dano_na_pista", "confirm_token": d["confirm_token"]}).status_code == 409


def test_consulta_nao_expoe_token(c):
    d = enviar(c).json()
    assert "confirm_token" not in c.get(f"/api/reports/{d['id']}").json()
    lista = c.get("/api/reports").json()
    assert any(r["id"] == d["id"] for r in lista)
    assert all("confirm_token" not in r for r in lista)


def test_filtros_da_listagem(c):
    d = enviar(c).json()
    assert any(r["id"] == d["id"] for r in c.get("/api/reports?status=recebido").json())
    assert all(r["id"] != d["id"] for r in c.get("/api/reports?status=encaminhado").json())
    assert c.get("/api/reports?status=inexistente").status_code == 422


def test_fluxo_completo_ate_ordem_de_servico(c):
    d = enviar(c).json()
    rid = d["id"]

    # O robô não encaminha o que a triagem ainda não liberou.
    assert c.patch(f"/robo/reports/{rid}/service-order", json={"service_order": "OS-1"}, headers=ROBO).status_code == 409

    r = c.patch(f"/api/reports/{rid}/status", json={"status": "em_triagem"}, headers=OPERADOR)
    assert r.json()["status"] == "em_triagem"

    fila = c.get("/robo/reports", headers=ROBO).json()
    assert any(x["id"] == rid for x in fila)

    r = c.patch(f"/robo/reports/{rid}/service-order", json={"service_order": "OS-123"}, headers=ROBO)
    assert (r.json()["status"], r.json()["service_order"]) == ("encaminhado", "OS-123")
    assert c.get(f"/api/reports/{rid}").json()["service_order"] == "OS-123"


def test_operador_nao_pula_etapas(c):
    rid = enviar(c).json()["id"]
    r = c.patch(f"/api/reports/{rid}/status", json={"status": "encaminhado"}, headers=OPERADOR)
    assert r.status_code == 409
    assert c.patch(f"/api/reports/{rid}/status", json={"status": "descartado"}, headers=OPERADOR).status_code == 200
    assert c.patch(f"/api/reports/{rid}/status", json={"status": "em_triagem"}, headers=OPERADOR).status_code == 409


def test_rotas_protegidas_exigem_token(c):
    rid = enviar(c).json()["id"]
    assert c.get("/robo/reports").status_code == 401
    assert c.get("/robo/reports", headers={"x-robo-token": "errado"}).status_code == 401
    assert c.get("/robo/reports", headers={"x-robo-token": "token-operador-teste"}).status_code == 401
    assert c.patch(f"/api/reports/{rid}/status", json={"status": "em_triagem"}).status_code == 401
    assert c.patch(f"/api/reports/{rid}/status", json={"status": "em_triagem"}, headers={"x-operador-token": "token-robo-teste"}).status_code == 401


def test_foto_pode_ser_baixada(c):
    rid = enviar(c).json()["id"]
    r = c.get(f"/api/reports/{rid}/image")
    assert r.status_code == 200 and r.content.startswith(b"\x89PNG")
    assert c.get("/api/reports/999999/image").status_code == 404


def test_rejeita_arquivo_que_nao_e_foto(c):
    r = c.post("/api/reports", data={"location": "Rua A"}, files={"photo": ("a.txt", b"oi", "text/plain")})
    assert r.status_code == 415


def test_rejeita_campos_invalidos(c):
    assert enviar(c, location="").status_code == 422
    assert enviar(c, latitude="200").status_code == 422
    assert enviar(c, category="vazamento").status_code == 422


def test_aceita_coordenadas_opcionais(c):
    d = enviar(c, latitude="-23.56", longitude="-46.65").json()
    assert (d["latitude"], d["longitude"]) == (-23.56, -46.65)


def test_metricas_expostas(c):
    enviar(c)
    texto = c.get("/metrics").text
    assert "zela_requisicoes_total" in texto and "zela_relatos_total" in texto


def test_data_sai_com_fuso_utc(c):
    d = enviar(c).json()
    assert d["created_at"].endswith("Z") or d["created_at"].endswith("+00:00")
    assert c.get(f"/api/reports/{d['id']}").json()["created_at"] == d["created_at"]


def _jpeg_com_gps_e_rotacao():
    exif = Image.Exif()
    exif[0x010F] = "FabricanteSecreto"  # Make
    exif[0x0112] = 6  # orientação: girar 90 graus
    exif[0x8825] = {1: "S", 2: (23.0, 33.0, 0.0), 3: "W", 4: (46.0, 38.0, 0.0)}  # GPS
    return _imagem("JPEG", tamanho=(8, 4), exif=exif)


def test_foto_perde_exif_e_gps_antes_de_ser_gravada(c):
    original = _jpeg_com_gps_e_rotacao()
    assert b"FabricanteSecreto" in original and Image.open(io.BytesIO(original)).getexif()

    r = c.post(
        "/api/reports",
        data={"location": "Rua Augusta, 100"},
        files={"photo": ("f.jpg", original, "image/jpeg")},
    )
    assert r.status_code == 201
    salvo = c.get(f"/api/reports/{r.json()['id']}/image").content
    assert b"FabricanteSecreto" not in salvo
    foto = Image.open(io.BytesIO(salvo))
    assert not dict(foto.getexif())  # sem Make, GPS ou orientação
    assert foto.size == (4, 8)  # a rotação do EXIF foi aplicada nos pixels


def test_png_com_texto_perde_os_metadados(c):
    saida = io.BytesIO()
    from PIL.PngImagePlugin import PngInfo

    info = PngInfo()
    info.add_text("Comment", "segredo-no-png")
    Image.new("RGB", (4, 4)).save(saida, format="PNG", pnginfo=info)
    r = c.post("/api/reports", data={"location": "Rua B, 2"}, files={"photo": ("f.png", saida.getvalue(), "image/png")})
    assert r.status_code == 201
    assert b"segredo-no-png" not in c.get(f"/api/reports/{r.json()['id']}/image").content


def test_rejeita_arquivo_que_finge_ser_foto(c):
    for conteudo, tipo in ((b"nao sou imagem", "image/png"), (PNG, "image/jpeg")):
        r = c.post("/api/reports", data={"location": "Rua C, 3"}, files={"photo": ("x", conteudo, tipo)})
        assert r.status_code == 400


def test_erro_nao_tratado_conta_como_500_nas_metricas(monkeypatch):
    def quebrar(*_):
        raise RuntimeError("falha simulada")

    monkeypatch.setattr(main, "buscar", quebrar)
    serie = main.REQUISICOES.labels("GET", "/api/reports/{report_id}", 500)
    antes = serie._value.get()
    with TestClient(app, raise_server_exceptions=False) as cliente:
        assert cliente.get("/api/reports/1").status_code == 500
    assert serie._value.get() == antes + 1


def test_id_fora_do_intervalo_do_banco_da_404_e_nao_500(c):
    for rid in (0, -1, 9999999999, 99999999999999999999):
        assert c.get(f"/api/reports/{rid}").status_code == 404
        assert c.get(f"/api/reports/{rid}/image").status_code == 404
