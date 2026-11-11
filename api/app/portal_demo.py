"""PORTAL DE DEMONSTRAÇÃO da fila de manutenção (alvo do robô UiPath).

Simula o sistema de destino que não tem API: login, formulário com anexo
e uma tela de confirmação com o número da ordem de serviço. O robô opera
estas páginas pela interface, como faria num portal real.

Não é um sistema oficial. Só funciona se PORTAL_DEMO_USUARIO e
PORTAL_DEMO_SENHA estiverem definidos (não há usuário padrão).

Os campos têm `id` fixo para os seletores do UiPath ficarem estáveis:
login (#usuario, #senha, #entrar), formulário (#endereco, #tipo, #descricao,
#referencia, #anexo, #enviar) e confirmação (#numero-os).
"""

import os
import secrets
import time
import uuid
from html import escape
from pathlib import Path

from fastapi import APIRouter, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from sqlalchemy import select

from .db import OrdemServico, SessionLocal

router = APIRouter(prefix="/portal-demo", include_in_schema=False)

COOKIE = "portal_sessao"
DURACAO_SESSAO = 8 * 3600
MAX_ANEXO = 5 * 1024 * 1024
TIPOS_ANEXO = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}
TIPOS_SERVICO = {
    "buraco_pavimento": "Buraco / pavimento",
    "calcada": "Calçada",
    "drenagem": "Boca de lobo / drenagem",
    "limpeza": "Limpeza / entulho",
    "iluminacao": "Iluminação pública",
    "outros": "Outros",
}

# Sessões em memória: suficiente para a demo (uma réplica). token -> (usuário, expira_em)
_sessoes: dict[str, tuple[str, float]] = {}


def _credenciais() -> tuple[str, str] | None:
    usuario, senha = os.getenv("PORTAL_DEMO_USUARIO", ""), os.getenv("PORTAL_DEMO_SENHA", "")
    return (usuario, senha) if usuario and senha else None


def _pasta_anexos() -> Path:
    pasta = Path(os.getenv("UPLOAD_DIR", "./uploads")) / "portal"
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta


def _usuario(request: Request) -> str | None:
    token = request.cookies.get(COOKIE, "")
    sessao = _sessoes.get(token)
    if not sessao or sessao[1] < time.time():
        _sessoes.pop(token, None)
        return None
    return sessao[0]


def _pagina(titulo: str, corpo: str, usuario: str | None = None, status: int = 200) -> HTMLResponse:
    sair = (
        f'<form method="post" action="/portal-demo/sair"><span>{escape(usuario)}</span> '
        f'<button class="botao secundario" id="sair" type="submit">Sair</button></form>'
        if usuario else ""
    )
    html = f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(titulo)} · Portal de manutenção (demonstração)</title>
<link rel="stylesheet" href="/estilo.css"></head>
<body>
<header class="topo portal"><div class="conteudo">
  <a href="/portal-demo/">Portal de manutenção</a>
  <nav aria-label="Portal" class="portal-nav">{'<a href="/portal-demo/ordens">Ordens</a>' if usuario else ''}{sair}</nav>
</div></header>
<main class="conteudo">
<div class="cartao aviso" role="note"><strong>Portal de demonstração.</strong> Não é um sistema oficial da prefeitura. Serve só para o robô do Zela abrir ordens de serviço de teste.</div>
{corpo}
</main></body></html>"""
    return HTMLResponse(html, status_code=status)


def _desativado() -> HTMLResponse:
    return _pagina("Indisponível", '<div class="cartao falha"><h1>Portal desativado</h1>'
                   "<p>Defina PORTAL_DEMO_USUARIO e PORTAL_DEMO_SENHA no servidor para usar o portal de demonstração.</p></div>",
                   status=503)


def _form_login(erro: str = "") -> str:
    aviso = f'<div class="cartao falha" role="alert" id="erro-login">{escape(erro)}</div>' if erro else ""
    return f"""<h1>Entrar</h1>{aviso}
<form class="cartao" method="post" action="/portal-demo/login">
  <div class="campo"><label for="usuario">Usuário</label><input id="usuario" name="usuario" type="text" autocomplete="username" required></div>
  <div class="campo"><label for="senha">Senha</label><input id="senha" name="senha" type="password" autocomplete="current-password" required></div>
  <button class="botao" id="entrar" type="submit">Entrar</button>
</form>"""


@router.get("/", response_class=HTMLResponse)
def inicio(request: Request):
    if not _credenciais():
        return _desativado()
    usuario = _usuario(request)
    if not usuario:
        return _pagina("Entrar", _form_login())
    return RedirectResponse("/portal-demo/nova", status_code=303)


@router.post("/login")
def login(request: Request, usuario: str = Form(""), senha: str = Form("")):
    cred = _credenciais()
    if not cred:
        return _desativado()
    ok = secrets.compare_digest(usuario.encode(), cred[0].encode()) & secrets.compare_digest(senha.encode(), cred[1].encode())
    if not ok:
        return _pagina("Entrar", _form_login("Usuário ou senha inválidos."), status=401)
    token = secrets.token_urlsafe(32)
    _sessoes[token] = (usuario, time.time() + DURACAO_SESSAO)
    resposta = RedirectResponse("/portal-demo/nova", status_code=303)
    resposta.set_cookie(COOKIE, token, max_age=DURACAO_SESSAO, httponly=True, samesite="strict",
                        secure=request.url.scheme == "https", path="/portal-demo")
    return resposta


@router.post("/sair")
def sair(request: Request):
    _sessoes.pop(request.cookies.get(COOKIE, ""), None)
    resposta = RedirectResponse("/portal-demo/", status_code=303)
    resposta.delete_cookie(COOKIE, path="/portal-demo")
    return resposta


def _form_ordem(erro: str = "") -> str:
    opcoes = "".join(f'<option value="{v}">{escape(r)}</option>' for v, r in TIPOS_SERVICO.items())
    aviso = f'<div class="cartao falha" role="alert" id="erro-ordem">{escape(erro)}</div>' if erro else ""
    return f"""<h1>Nova ordem de serviço</h1>{aviso}
<form class="cartao" method="post" action="/portal-demo/ordens" enctype="multipart/form-data">
  <div class="campo"><label for="endereco">Endereço ou ponto de referência</label><input id="endereco" name="endereco" type="text" required minlength="3" maxlength="200"></div>
  <div class="campo"><label for="tipo">Tipo de serviço</label><select id="tipo" name="tipo" required><option value="">Selecione</option>{opcoes}</select></div>
  <div class="campo"><label for="descricao">Descrição</label><textarea id="descricao" name="descricao" maxlength="1000"></textarea></div>
  <div class="campo"><label for="referencia">Referência externa (opcional)</label><input id="referencia" name="referencia" type="text" maxlength="40"></div>
  <div class="campo"><label for="anexo">Foto (JPEG, PNG ou WebP, até 5 MB)</label><input id="anexo" name="anexo" type="file" accept="image/jpeg,image/png,image/webp"></div>
  <button class="botao" id="enviar" type="submit">Abrir ordem de serviço</button>
</form>"""


@router.get("/nova", response_class=HTMLResponse)
def nova(request: Request):
    if not _credenciais():
        return _desativado()
    usuario = _usuario(request)
    if not usuario:
        return RedirectResponse("/portal-demo/", status_code=303)
    return _pagina("Nova ordem", _form_ordem(), usuario)


@router.post("/ordens")
async def criar_ordem(
    request: Request,
    endereco: str = Form(""),
    tipo: str = Form(""),
    descricao: str = Form(""),
    referencia: str = Form(""),
    anexo: UploadFile | None = File(None),
):
    if not _credenciais():
        return _desativado()
    usuario = _usuario(request)
    if not usuario:
        return RedirectResponse("/portal-demo/", status_code=303)

    endereco, descricao, referencia = endereco.strip(), descricao.strip()[:1000], referencia.strip()[:40]
    if len(endereco) < 3 or len(endereco) > 200:
        return _pagina("Nova ordem", _form_ordem("Informe o endereço (3 a 200 caracteres)."), usuario, 422)
    if tipo not in TIPOS_SERVICO:
        return _pagina("Nova ordem", _form_ordem("Selecione o tipo de serviço."), usuario, 422)

    nome_anexo = None
    if anexo is not None and anexo.filename:
        extensao = TIPOS_ANEXO.get(anexo.content_type or "")
        conteudo = await anexo.read(MAX_ANEXO + 1)
        if not extensao or not conteudo or len(conteudo) > MAX_ANEXO:
            return _pagina("Nova ordem", _form_ordem("Anexo inválido: envie uma imagem JPEG, PNG ou WebP de até 5 MB."), usuario, 422)
        nome_anexo = f"{uuid.uuid4().hex}{extensao}"
        (_pasta_anexos() / nome_anexo).write_bytes(conteudo)

    with SessionLocal() as db:
        ordem = OrdemServico(endereco=endereco, tipo=tipo, descricao=descricao,
                             referencia_externa=referencia, anexo=nome_anexo, criada_por=usuario)
        db.add(ordem)
        db.commit()
        db.refresh(ordem)
        oid = ordem.id
    return RedirectResponse(f"/portal-demo/ordens/{oid}", status_code=303)


@router.get("/ordens/{oid}", response_class=HTMLResponse)
def ver_ordem(oid: int, request: Request):
    if not _credenciais():
        return _desativado()
    usuario = _usuario(request)
    if not usuario:
        return RedirectResponse("/portal-demo/", status_code=303)
    with SessionLocal() as db:
        o = db.get(OrdemServico, oid)
        if not o:
            return _pagina("Não encontrada", '<div class="cartao falha"><h1>Ordem não encontrada</h1></div>', usuario, 404)
        corpo = f"""<div class="cartao sucesso" id="confirmacao">
<h1>Ordem de serviço registrada</h1>
<p>Número da ordem de serviço:</p>
<p class="protocolo"><strong id="numero-os">{o.numero}</strong></p>
<dl class="detalhes">
  <dt>Endereço</dt><dd id="os-endereco">{escape(o.endereco)}</dd>
  <dt>Tipo</dt><dd id="os-tipo">{escape(TIPOS_SERVICO.get(o.tipo, o.tipo))}</dd>
  <dt>Referência externa</dt><dd id="os-referencia">{escape(o.referencia_externa or "—")}</dd>
  <dt>Anexo</dt><dd>{"foto recebida" if o.anexo else "sem foto"}</dd>
</dl>
<div class="acoes"><a class="botao" id="nova-ordem" href="/portal-demo/nova">Nova ordem</a></div>
</div>"""
    return _pagina(o.numero if o else "Ordem", corpo, usuario)


@router.get("/ordens", response_class=HTMLResponse)
def listar_ordens(request: Request):
    if not _credenciais():
        return _desativado()
    usuario = _usuario(request)
    if not usuario:
        return RedirectResponse("/portal-demo/", status_code=303)
    with SessionLocal() as db:
        ordens = db.scalars(select(OrdemServico).order_by(OrdemServico.id.desc()).limit(200)).all()
        linhas = "".join(
            f'<tr><td><a href="/portal-demo/ordens/{o.id}">{o.numero}</a></td><td>{o.criada_em:%d/%m/%Y %H:%M}</td>'
            f"<td>{escape(TIPOS_SERVICO.get(o.tipo, o.tipo))}</td><td>{escape(o.endereco)}</td>"
            f"<td>{escape(o.referencia_externa or '—')}</td></tr>"
            for o in ordens
        )
    tabela = (f'<div class="tabela-rolagem"><table id="lista-ordens"><thead><tr><th>Número</th><th>Criada (UTC)</th><th>Tipo</th>'
              f"<th>Endereço</th><th>Referência</th></tr></thead><tbody>{linhas}</tbody></table></div>"
              if linhas else "<p>Nenhuma ordem ainda.</p>")
    return _pagina("Ordens", f'<h1>Ordens de serviço</h1><div class="cartao">{tabela}</div>', usuario)


@router.get("", include_in_schema=False)
def sem_barra():
    return Response(status_code=307, headers={"Location": "/portal-demo/"})
