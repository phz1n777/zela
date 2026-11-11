import os
import secrets
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from fastapi import Depends, FastAPI, File, Form, Header, HTTPException, Query, Request, UploadFile
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select
from sqlalchemy.orm import Session

from .db import Report, SessionLocal, init_db
from . import portal_demo
from .services import imagem, vision

UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "./uploads"))
# App do cidadão e painel (pasta web/ do repositório). No container: /app/web.
WEB_DIR = Path(os.getenv("WEB_DIR", Path(__file__).resolve().parents[2] / "web"))

# Só recursos do próprio domínio. blob: permite a prévia da foto antes do envio.
CABECALHOS_SEGURANCA = {
    "Content-Security-Policy": (
        "default-src 'self'; img-src 'self' blob: data:; style-src 'self'; script-src 'self'; "
        "connect-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'; form-action 'self'"
    ),
    "X-Content-Type-Options": "nosniff",
    "Referrer-Policy": "no-referrer",
    "Permissions-Policy": "camera=(self), geolocation=(self), microphone=()",
}
MAX_FOTO_BYTES = 5 * 1024 * 1024
TIPOS_FOTO = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}

# Só dano_na_pista tem sugestão automática. As outras são escolha manual do cidadão.
Categoria = Literal["dano_na_pista", "calcada", "bueiro", "lixo", "iluminacao", "outro"]
Status = Literal["recebido", "em_triagem", "encaminhado", "descartado"]
Origem = Literal["cidadao", "demo"]

# Transições que o operador da triagem pode fazer. "encaminhado" é só pelo robô.
TRANSICOES_OPERADOR = {
    "recebido": {"em_triagem", "descartado"},
    "em_triagem": {"descartado"},
}

# Métricas de ouro (latência, tráfego, erros) para o Prometheus.
REQUISICOES = Counter("zela_requisicoes_total", "Requisições HTTP", ["metodo", "rota", "status"])
LATENCIA = Histogram("zela_latencia_segundos", "Latência das requisições", ["rota"])
RELATOS = Counter("zela_relatos_total", "Relatos criados", ["cv_label"])


@asynccontextmanager
async def lifespan(_: FastAPI):
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    init_db()
    yield


app = FastAPI(title="Zela API", version="0.2.0", lifespan=lifespan)


def _registrar(request: Request, status: int, inicio: float) -> None:
    caminho = getattr(request.scope.get("route"), "path", "desconhecida")
    LATENCIA.labels(caminho).observe(time.perf_counter() - inicio)
    REQUISICOES.labels(request.method, caminho, status).inc()


@app.middleware("http")
async def medir(request: Request, call_next):
    inicio = time.perf_counter()
    try:
        resposta = await call_next(request)
    except Exception:
        # Erro não tratado vira 500 para o cliente: conta como erro nas métricas antes de seguir.
        _registrar(request, 500, inicio)
        raise
    _registrar(request, resposta.status_code, inicio)
    for nome, valor in CABECALHOS_SEGURANCA.items():
        resposta.headers.setdefault(nome, valor)
    return resposta


def sessao():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _exigir(nome_env: str, recebido: str, quem: str) -> None:
    esperado = os.getenv(nome_env, "")
    if not esperado or not secrets.compare_digest(recebido, esperado):
        raise HTTPException(status_code=401, detail=f"token do {quem} inválido")


def exigir_token_robo(x_robo_token: str = Header(default="")) -> None:
    """Só o robô RPA lista a fila e grava a ordem de serviço."""
    _exigir("ROBO_TOKEN", x_robo_token, "robô")


def exigir_token_operador(x_operador_token: str = Header(default="")) -> None:
    """Só a equipe de triagem muda o status de um relato."""
    _exigir("OPERADOR_TOKEN", x_operador_token, "operador")


ID_MAXIMO = 2**31 - 1  # limite do inteiro do banco; ids fora dele não existem


def buscar(db: Session, report_id: int) -> Report:
    report = db.get(Report, report_id) if 0 < report_id <= ID_MAXIMO else None
    if not report:
        raise HTTPException(status_code=404, detail="relato não encontrado")
    return report


class ReportOut(BaseModel):
    id: int
    created_at: datetime
    location: str
    latitude: float | None
    longitude: float | None
    description: str
    category: str
    status: str
    source: str
    cv_label: str | None
    cv_confidence: float | None
    cv_model: str | None
    cv_reviewed: bool
    service_order: str | None

    model_config = {"from_attributes": True}

    @field_validator("created_at")
    @classmethod
    def em_utc(cls, valor: datetime) -> datetime:
        # O SQLite devolve a data sem fuso; ela foi gravada em UTC.
        return valor if valor.tzinfo else valor.replace(tzinfo=timezone.utc)


class ReportCriado(ReportOut):
    # Devolvido só nesta resposta. O app guarda e usa para confirmar a categoria.
    confirm_token: str


class ConfirmacaoIn(BaseModel):
    category: Categoria
    confirm_token: str


class StatusIn(BaseModel):
    status: Status


class OrdemServicoIn(BaseModel):
    service_order: str = Field(min_length=1, max_length=40)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/api/reports", response_model=ReportCriado, status_code=201)
async def criar_relato(
    photo: UploadFile = File(...),
    location: str = Form(..., min_length=3, max_length=200),
    description: str = Form("", max_length=500),
    latitude: float | None = Form(None, ge=-90, le=90),
    longitude: float | None = Form(None, ge=-180, le=180),
    category: Categoria | None = Form(None),
    db: Session = Depends(sessao),
):
    extensao = TIPOS_FOTO.get(photo.content_type or "")
    if not extensao:
        raise HTTPException(status_code=415, detail="envie uma foto JPEG, PNG ou WebP")
    conteudo = await photo.read(MAX_FOTO_BYTES + 1)
    if len(conteudo) > MAX_FOTO_BYTES:
        raise HTTPException(status_code=413, detail="foto maior que 5 MB")
    if not conteudo:
        raise HTTPException(status_code=400, detail="foto vazia")

    try:
        conteudo = imagem.limpar(conteudo, photo.content_type)
    except imagem.FotoInvalida as erro:
        raise HTTPException(status_code=400, detail=str(erro)) from erro

    # Nome gerado por nós: nunca usamos o nome de arquivo enviado pelo cliente.
    caminho = UPLOAD_DIR / f"{uuid.uuid4().hex}{extensao}"
    caminho.write_bytes(conteudo)

    sugestao = vision.sugerir(conteudo)
    if category is None:
        category = "dano_na_pista" if sugestao.label == vision.ROTULO_DANO else "outro"

    report = Report(
        location=location.strip(),
        latitude=latitude,
        longitude=longitude,
        description=description.strip(),
        image=caminho.name,
        category=category,
        cv_label=sugestao.label,
        cv_confidence=sugestao.confidence,
        cv_model=sugestao.model,
        confirm_token=secrets.token_urlsafe(24),
    )
    db.add(report)
    db.commit()
    db.refresh(report)
    RELATOS.labels(sugestao.label or "sem_modelo").inc()
    return report


@app.post("/api/reports/{report_id}/confirmation", response_model=ReportOut)
def confirmar_categoria(report_id: int, dados: ConfirmacaoIn, db: Session = Depends(sessao)):
    """O cidadão confirma ou corrige a sugestão. Só vale uma vez, antes da triagem."""
    report = buscar(db, report_id)
    if not secrets.compare_digest(dados.confirm_token, report.confirm_token):
        raise HTTPException(status_code=403, detail="token de confirmação inválido")
    if report.cv_reviewed or report.status != "recebido":
        raise HTTPException(status_code=409, detail="relato já confirmado ou em triagem")
    report.category = dados.category
    report.cv_reviewed = True
    db.commit()
    db.refresh(report)
    return report


@app.get("/api/reports", response_model=list[ReportOut])
def listar_relatos(
    status: Status | None = None,
    category: Categoria | None = None,
    source: Origem | None = None,
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(sessao),
):
    consulta = select(Report).order_by(Report.id.desc()).limit(limit)
    if status:
        consulta = consulta.where(Report.status == status)
    if category:
        consulta = consulta.where(Report.category == category)
    if source:
        consulta = consulta.where(Report.source == source)
    return db.scalars(consulta).all()


@app.get("/api/reports/{report_id}", response_model=ReportOut)
def ver_relato(report_id: int, db: Session = Depends(sessao)):
    return buscar(db, report_id)


@app.get("/api/reports/{report_id}/image")
def ver_foto(report_id: int, db: Session = Depends(sessao)):
    report = buscar(db, report_id)
    caminho = UPLOAD_DIR / Path(report.image).name
    if not caminho.is_file():
        raise HTTPException(status_code=404, detail="foto não encontrada")
    return FileResponse(caminho)


@app.patch(
    "/api/reports/{report_id}/status",
    response_model=ReportOut,
    dependencies=[Depends(exigir_token_operador)],
)
def mudar_status(report_id: int, dados: StatusIn, db: Session = Depends(sessao)):
    report = buscar(db, report_id)
    if dados.status not in TRANSICOES_OPERADOR.get(report.status, set()):
        raise HTTPException(
            status_code=409, detail=f"não é possível ir de {report.status} para {dados.status}"
        )
    report.status = dados.status
    db.commit()
    db.refresh(report)
    return report


@app.get(
    "/robo/reports",
    response_model=list[ReportOut],
    dependencies=[Depends(exigir_token_robo)],
)
def fila_do_robo(status: Status = "em_triagem", db: Session = Depends(sessao)):
    """Fila de trabalho do UiPath: por padrão, os relatos que a triagem liberou."""
    consulta = select(Report).where(Report.status == status).order_by(Report.id)
    return db.scalars(consulta).all()


@app.patch(
    "/robo/reports/{report_id}/service-order",
    response_model=ReportOut,
    dependencies=[Depends(exigir_token_robo)],
)
def gravar_ordem_servico(report_id: int, dados: OrdemServicoIn, db: Session = Depends(sessao)):
    report = buscar(db, report_id)
    if report.status != "em_triagem":
        raise HTTPException(status_code=409, detail="só relatos em triagem podem ser encaminhados")
    report.service_order = dados.service_order
    report.status = "encaminhado"
    db.commit()
    db.refresh(report)
    return report


# Portal de demonstração da fila de manutenção (alvo do robô UiPath).
app.include_router(portal_demo.router)

# Por último: tudo que não é API cai no app web estático (index.html, painel.html...).
if WEB_DIR.is_dir():
    app.mount("/", StaticFiles(directory=WEB_DIR, html=True), name="web")
