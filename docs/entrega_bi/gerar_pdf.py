"""Gera o PDF único de BI & Startup Development: Lean Canvas, modelo de negócio e links.

1. Preencha links.json (vídeo, URL do MVP, repositório, território, equipe).
2. Rode: python3 gerar_pdf.py
3. Saída: Zela_BI_Startup.pdf e Zela_BI_Startup.html, nesta pasta.

O conteúdo segue docs/lean_canvas.md e docs/modelo_de_negocio.md. Se mudar lá, mude aqui também.
Precisa do Google Chrome ou do Chromium instalado (usado para imprimir o PDF).
"""

import json
import shutil
import subprocess
import sys
import tempfile
from html import escape
from pathlib import Path

AQUI = Path(__file__).resolve().parent
L = json.loads((AQUI / "links.json").read_text(encoding="utf-8"))


def link(chave, rotulo):
    url = L.get(chave, "").strip()
    if not url:
        return f'<span class="falta">[preencher {escape(rotulo)} em links.json]</span>'
    return f'<a href="{escape(url, quote=True)}">{escape(url)}</a>'


def bloco(titulo, status, itens, classe=""):
    lis = "".join(f"<li>{i}</li>" for i in itens)
    return f'<section class="b {classe}"><h3>{titulo} <span class="st">{status}</span></h3><ul>{lis}</ul></section>'


territorio = escape(L.get("territorio_piloto") or "região piloto a definir")

canvas = f"""
<div class="canvas">
{bloco("1 · Problema", "🔶 sim.", [
    "Quem circula pelo território vê danos na via e não sabe onde relatar nem o que informar.",
    "Relatos chegam dispersos, sem foto, local ou categoria.",
    "Quem relatou não sabe se foi encaminhado.",
    "<em>Alternativas:</em> SP156, WhatsApp, e-mail, redes sociais."], "problema")}
{bloco("4 · Solução", "✅ técnica", [
    "Formulário sem cadastro aberto por QR.",
    "Visão sugere <b>dano na pista</b>; cidadão confirma.",
    "Painel de triagem + robô abre a OS.",
    "Indicadores por período (DAG)."], "solucao")}
{bloco("8 · Métricas-chave", "🔶", [
    "Relatos que chegam ao painel.", "% de sugestões confirmadas.",
    "Tempo do relato até a OS.", "Leituras do QR por placa."], "metricas")}
{bloco("3 · Proposta única de valor", "🔶", [
    "<b>“Fotografe o dano, confirme a sugestão e acompanhe o encaminhamento.”</b>",
    "Para quem administra: fila única com foto, local, status e histórico como evidência.",
    "<em>Alto nível:</em> um “protocolo com foto” para a zeladoria do território."], "puv")}
{bloco("9 · Vantagem injusta", "⬜", [
    "Ainda não há.", "Candidato: histórico de relatos com foto e local do território."], "vantagem")}
{bloco("5 · Canais", "⬜", [
    "Placas com QR nos pontos (Maker Lab).", "Piloto gratuito de 4 semanas.", "Venda consultiva com o relatório do piloto."], "canais")}
{bloco("2 · Segmentos", "🔶 sim.", [
    "<b>Usuário (grátis):</b> quem circula a pé, de bicicleta, de carro ou em cadeira de rodas.",
    "<b>Comprador:</b> campus e parque empresarial; condomínio com preço menor.",
    "<em>Early adopter:</em> facilities de campus que presta contas à diretoria."], "segmentos")}
{bloco("7 · Estrutura de custos", "🔶", [
    "Nuvem ≈ <b>US$ 30–60/mês (≈ R$ 250)</b>: container, banco, registro e logs.",
    "Por território: suporte ≈ R$ 120/mês; implantação ≈ R$ 660 (placas + instalação).",
    "Ao escalar: licença de RPA e LLM pago."], "custos")}
{bloco("6 · Fontes de receita", "🔶 sim.", [
    "Assinatura <b>por território</b>, paga pelo comprador; cidadão nunca paga.",
    "<b>Preço por segmento:</b> R$ 400/mês campus e parque (contrato anual); R$ 200/mês condomínio.",
    "Com R$ 400, 1 território cobre o fixo; implantação paga em ~2,4 meses."], "receita")}
</div>
<p class="leg">✅ validado com evidência · 🔶 parcialmente validado · ⬜ hipótese · <b>sim.</b> = sinal vindo de entrevistas <b>simuladas</b> (fictícias, autorizadas pelo professor), não de pessoas reais</p>
"""

html = f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><title>Zela · BI & Startup Development</title>
<style>
@page {{ size: A4; margin: 14mm; }}
@page paisagem {{ size: A4 landscape; margin: 10mm; }}
body {{ font: 10.5pt/1.45 "Segoe UI", Roboto, Arial, sans-serif; color: #1c1b19; }}
h1 {{ font-size: 20pt; margin: 0 0 4px; color: #0b5d4b; }}
h2 {{ font-size: 13.5pt; color: #0b5d4b; border-bottom: 2px solid #0b5d4b; padding-bottom: 2px; margin: 18px 0 8px; }}
.sub {{ color: #55524c; margin: 0 0 12px; }}
a {{ color: #0b5d4b; }}
.falta {{ color: #a1121d; font-weight: 600; }}
table {{ border-collapse: collapse; width: 100%; margin: 6px 0 10px; font-size: 9.5pt; }}
th, td {{ border: 1px solid #d6d2c8; padding: 4px 6px; text-align: left; vertical-align: top; }}
th {{ background: #e3f1ec; }}
.destaque td {{ background: #fdf0e4; font-weight: 600; }}
.pag-canvas {{ page: paisagem; break-before: page; }}
.canvas {{ display: grid; grid-template-columns: repeat(10, 1fr); grid-template-rows: 1fr 1fr auto;
          gap: 4px; height: 150mm; }}
.b {{ border: 1.5px solid #0b5d4b; border-radius: 6px; padding: 5px 7px; overflow: hidden; }}
.b h3 {{ margin: 0 0 3px; font-size: 10pt; color: #0b5d4b; display: flex; justify-content: space-between; }}
.b ul {{ margin: 0; padding-left: 14px; font-size: 8.6pt; }}
.b li {{ margin-bottom: 2px; }}
.st {{ font-weight: 400; font-size: 8.5pt; color: #55524c; }}
.problema {{ grid-column: 1 / 3; grid-row: 1 / 3; }}
.solucao {{ grid-column: 3 / 5; grid-row: 1; }}
.metricas {{ grid-column: 3 / 5; grid-row: 2; }}
.puv {{ grid-column: 5 / 7; grid-row: 1 / 3; background: #e3f1ec; }}
.vantagem {{ grid-column: 7 / 9; grid-row: 1; }}
.canais {{ grid-column: 7 / 9; grid-row: 2; }}
.segmentos {{ grid-column: 9 / 11; grid-row: 1 / 3; }}
.custos {{ grid-column: 1 / 6; grid-row: 3; }}
.receita {{ grid-column: 6 / 11; grid-row: 3; }}
.leg {{ font-size: 8.5pt; color: #55524c; margin: 4px 0 0; }}
.nota {{ font-size: 9pt; color: #55524c; }}
.quebra {{ break-before: page; }}
</style></head><body>

<h1>Zela: Zeladoria Urbana por Foto</h1>
<p class="sub">Global Solution 2026.2 · CitizenTech · Business Intelligence &amp; Startup Development · Pitch de Negócio + MVP</p>

<h2>Links</h2>
<table>
<tr><th>Vídeo-pitch (até 5 min)</th><td>{link("video_pitch", "link do vídeo")}</td></tr>
<tr><th>MVP (URL pública)</th><td>{link("mvp_url", "URL do MVP")}</td></tr>
<tr><th>Repositório</th><td>{link("repositorio", "link do repositório")}</td></tr>
<tr><th>Equipe</th><td>{escape(L.get("equipe", ""))}</td></tr>
<tr><th>Território piloto</th><td>{territorio}</td></tr>
</table>

<h2>Ficha técnica do MVP</h2>
<table>
<tr><th>Cidadão e território</th><td>Quem circula a pé, de bicicleta, de carro ou em cadeira de rodas pelo {territorio}</td></tr>
<tr><th>Problema</th><td>Danos na via ficam sem relato claro porque as pessoas não sabem onde relatar, o que informar ou se o problema já foi encaminhado</td></tr>
<tr><th>Proposta de valor</th><td>Transformar uma foto e um local em uma ocorrência estruturada e acompanhável</td></tr>
<tr><th>Arquitetura</th><td>App web (PWA) · API FastAPI · Visão (YOLO11n no RDD2022) · Postgres · Airflow · Robô UiPath · FonteBot (GenAI) · Placa com QR · Docker, Terraform e GitHub Actions</td></tr>
<tr><th>Fontes de dados</th><td>Relatos do piloto · fotos locais · RDD2022 (CC BY 4.0) · registros simulados marcados como demonstração</td></tr>
<tr><th>Modelos de IA</th><td>YOLO11n (sugestão de “dano na pista”, sempre com confirmação humana) · LLM via OpenRouter no FonteBot</td></tr>
<tr><th>Indicadores</th><td>Conclusão do fluxo · concordância da visão · tempo do relato até a OS · acesso pelo QR</td></tr>
<tr><th>ODS</th><td>11 (cidades sustentáveis) · 9 (infraestrutura) · 13 (clima, como próximo passo)</td></tr>
</table>

<div class="pag-canvas">
<h2>Lean Canvas consolidado</h2>
{canvas}
</div>

<div class="quebra"></div>
<h2>O que mudou pelo caminho</h2>
<table>
<tr><th>Momento</th><th>O que acreditávamos</th><th>O que aprendemos</th><th>O que mudou</th></tr>
<tr><td>Proposta inicial → revisada</td><td>IA “classifica e protocola” vários problemas na prefeitura</td><td>O dataset só cobre dano na pista; o portal oficial exige prova de viabilidade</td><td>Uma categoria automática com confirmação humana; encaminhamento para fila de demonstração; sem promessa de reparo</td></tr>
<tr><td>Entrevistas <b>simuladas</b></td><td>Preço único de R$ 400; RPA como integração padrão</td><td>Condomínio paga menos (R$ 150–250); campus e parque querem a OS no sistema que já usam; parque prefere API</td><td>Preço por segmento; campus e parque como early adopters; API quando houver, RPA quando não; acessibilidade como próximo passo</td></tr>
</table>

<h2>Entrevistas simuladas (síntese)</h2>
<p class="nota"><b>Simulação:</b> 4 entrevistas fictícias, autorizadas pelo professor para exercitar a validação no prazo. Os nomes são inventados e não são clientes nem tração. A íntegra está em docs/entrevistas_simuladas.md.</p>
<table>
<tr><th>Perfil (fictício)</th><th>Sinal principal</th></tr>
<tr><td>Facilities de campus</td><td>3–4 h/semana organizando avisos; equipe vai ao lugar errado; aceita R$ 400–600 em contrato anual com relatório mensal; quer a OS no sistema de chamados</td></tr>
<tr><td>Síndico de condomínio</td><td>Morador quer ver o status; não precisa de robô; R$ 400 é caro, aprovaria R$ 150–250</td></tr>
<tr><td>Operações de parque empresarial</td><td>Foto e histórico valem como evidência; aceita R$ 400–800; prefere integração por API; exige contrato e LGPD</td></tr>
<tr><td>Estudante usuário de cadeira de rodas</td><td>Usaria o QR só sem login e sem app; pediu para marcar “bloqueia rampa”</td></tr>
</table>

<h2>Modelo de negócio</h2>
<table>
<tr><th>Proposta de valor</th><td><b>Cidadão:</b> relato em menos de 1 minuto, sem cadastro, com protocolo e status. <b>Administração:</b> fila única com foto e local, triagem em um clique e OS aberta pelo robô. <b>Manutenção:</b> foto e referência na própria OS.</td></tr>
<tr><th>Receita e preço</th><td>Assinatura mensal por território, paga pelo comprador. O cidadão nunca paga. Preço por segmento: <b>R$ 400/mês</b> para campus e parque empresarial, <b>R$ 200/mês</b> para condomínio. Ajustado pelas entrevistas simuladas e ainda não validado com compradores reais.</td></tr>
<tr><th>Canais</th><td>Piloto gratuito de 4 semanas → placas com QR nos pontos → venda consultiva com o relatório do piloto</td></tr>
<tr><th>Métricas-chave</th><td>Conclusão do fluxo · concordância da visão · tempo até a OS · leituras do QR · retenção após o piloto</td></tr>
</table>

<h2>A conta (estimativa)</h2>
<p class="nota">Premissas: US$ 1 = R$ 5,50 · hora da equipe = R$ 60 · infraestrutura compartilhada entre territórios · custo de nuvem estimado para o ambiente publicado (Azure, spaincentral), sem fatura real.</p>
<table>
<tr><th>Custo fixo mensal (compartilhado)</th><th>Estimativa</th></tr>
<tr><td>Container App (0,5 vCPU, réplica sempre ligada)</td><td>maior parcela</td></tr>
<tr><td>PostgreSQL Flexible B1ms + 32 GB</td><td>parcela fixa principal</td></tr>
<tr><td>Container Registry, logs e alerta</td><td>pequena</td></tr>
<tr><td>Domínio .com.br</td><td>~ R$ 4</td></tr>
<tr class="destaque"><td>Total fixo (estimativa do ambiente publicado)</td><td>US$ 30–60 ≈ R$ 165–330/mês · usamos R$ 250</td></tr>
</table>
<table>
<tr><th>Preço/mês</th><th>Margem por território (− R$ 120 de suporte)</th><th>Territórios para cobrir o fixo (R$ 250; pior caso R$ 330)</th><th>Meses para pagar a implantação (R$ 660)</th></tr>
<tr><td>R$ 200</td><td>R$ 80</td><td>4 (5)</td><td>~8,3</td></tr>
<tr class="destaque"><td>R$ 400</td><td>R$ 280</td><td>1 (2)</td><td>~2,4</td></tr>
<tr><td>R$ 800</td><td>R$ 680</td><td>1</td><td>~1,0</td></tr>
</table>
<p>Com R$ 400, <b>1 território cobre a nuvem</b> no cenário médio (2 no pior caso). Com 5 territórios, a receita (R$ 2.000) contra o custo (≈ R$ 850) deixa ≈ R$ 1.150/mês. A conta fecha <b>se a hipótese de preço se confirmar</b>, e é isso que as conversas com compradores testam.</p>

<h2>Limites declarados</h2>
<p class="nota">Não prometemos reparo nem prazo. Não há detecção automática de lixo, bueiros ou calçadas. Não há integração oficial antes da prova de viabilidade. Os dados simulados estão marcados como demonstração. A classificação apoia a triagem e não substitui a avaliação humana.</p>
</body></html>
"""

saida_html = AQUI / "Zela_BI_Startup.html"
saida_html.write_text(html, encoding="utf-8")

chrome = next((c for c in ("google-chrome", "chromium", "chromium-browser", "chrome") if shutil.which(c)), None)
if not chrome:
    sys.exit(f"HTML gerado em {saida_html}. Instale o Chrome/Chromium ou imprima o HTML como PDF pelo navegador.")
with tempfile.TemporaryDirectory() as perfil:
    subprocess.run([chrome, "--headless=new", "--disable-gpu", "--no-first-run", f"--user-data-dir={perfil}",
                    "--no-pdf-header-footer", f"--print-to-pdf={AQUI / 'Zela_BI_Startup.pdf'}", saida_html.as_uri()],
                   check=True, capture_output=True, timeout=120)
print("PDF gerado:", AQUI / "Zela_BI_Startup.pdf")
