"""Gera o PDF único de Secure DevOps & Cloud Computing (Deploy Blindado).

Rode: python3 gerar_pdf.py
Saída: Zela_DevSecOps.pdf e Zela_DevSecOps.html, nesta pasta. Precisa do Google Chrome ou Chromium
(usado para imprimir o PDF). O conteúdo resume infra/, docs/arquitetura.md e docs/custos_e_lgpd.md.
"""

import base64
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
REPO = "https://github.com/phz1n777/zela"
MVP = "https://ca-zela-uylmp.jollyglacier-50c67627.spaincentral.azurecontainerapps.io"
BLOB = f"{REPO}/blob/main"

grafana = base64.b64encode((RAIZ / "infra/evidencias/grafana_4_sinais.jpg").read_bytes()).decode()

DIAGRAMA = """
<svg viewBox="0 0 900 470" xmlns="http://www.w3.org/2000/svg" font-family="Arial, sans-serif" font-size="12">
  <defs><marker id="s" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
    <path d="M0 0L10 5L0 10z" fill="#4a5568"/></marker></defs>
  <style>.c{fill:#fff;stroke:#0b5d4b;stroke-width:1.5}.g{fill:#e3f1ec;stroke:#0b5d4b;stroke-width:1.5}
  .z{fill:#e8f0fb;stroke:#2b5fa8;stroke-width:1.5}.l{stroke:#4a5568;stroke-width:1.4;fill:none;marker-end:url(#s)}
  .t{fill:#1c1b19}.m{fill:#55524c;font-size:10.5px}.h{font-weight:700;fill:#0b5d4b}</style>
  <rect x="8" y="8" width="150" height="150" rx="8" class="c"/><text x="20" y="28" class="h">Cidadão e equipe</text>
  <rect x="20" y="40" width="126" height="32" rx="5" class="g"/><text x="30" y="60" class="t">App web (PWA)</text>
  <rect x="20" y="80" width="126" height="32" rx="5" class="g"/><text x="30" y="100" class="t">Painel de triagem</text>
  <rect x="20" y="120" width="126" height="30" rx="5" class="g"/><text x="30" y="139" class="t">Robô UiPath</text>

  <rect x="200" y="8" width="480" height="300" rx="8" class="z"/><text x="212" y="28" class="h">Azure (spaincentral), criado por Terraform</text>
  <rect x="215" y="42" width="200" height="82" rx="6" class="c"/><text x="225" y="62" class="t" font-weight="700">Container App (HTTPS)</text>
  <text x="225" y="80" class="m">API FastAPI + app web</text><text x="225" y="95" class="m">usuário não-root, tokens em secrets</text>
  <text x="225" y="110" class="m">/health e /metrics</text>
  <rect x="470" y="42" width="195" height="82" rx="6" class="c"/><text x="480" y="62" class="t" font-weight="700">PostgreSQL 16 (Flexible)</text>
  <text x="480" y="80" class="m">B1ms, backup de 7 dias</text><text x="480" y="95" class="m">TLS + senha; acesso só de serviços</text>
  <text x="480" y="110" class="m">do Azure (sem 0.0.0.0/0 admin)</text>
  <rect x="215" y="150" width="200" height="60" rx="6" class="c"/><text x="225" y="170" class="t" font-weight="700">Container Registry (ACR)</text>
  <text x="225" y="188" class="m">pull por identidade gerenciada</text>
  <rect x="470" y="150" width="195" height="60" rx="6" class="c"/><text x="480" y="170" class="t" font-weight="700">Log Analytics</text>
  <text x="480" y="188" class="m">logs do contêiner, 30 dias</text>
  <rect x="470" y="230" width="195" height="62" rx="6" class="c"/><text x="480" y="250" class="t" font-weight="700">Alerta de 5xx</text>
  <text x="480" y="268" class="m">consulta nos logs, e-mail à equipe</text><text x="480" y="282" class="m">(Azure Monitor)</text>

  <rect x="715" y="8" width="177" height="150" rx="8" class="c"/><text x="727" y="28" class="h">Observabilidade (local)</text>
  <rect x="727" y="40" width="153" height="32" rx="5" class="g"/><text x="737" y="60" class="t">Prometheus</text>
  <rect x="727" y="80" width="153" height="62" rx="5" class="g"/><text x="737" y="100" class="t">Grafana</text>
  <text x="737" y="116" class="m">4 sinais de ouro</text><text x="737" y="130" class="m">lê /metrics do Azure</text>

  <rect x="8" y="340" width="672" height="122" rx="8" class="c"/><text x="20" y="360" class="h">Pipeline (GitHub Actions) a cada push</text>
  <rect x="20" y="372" width="96" height="40" rx="5" class="g"/><text x="28" y="389" class="t">Testes</text><text x="28" y="403" class="m">pytest</text>
  <rect x="126" y="372" width="96" height="40" rx="5" class="g"/><text x="134" y="389" class="t">Gitleaks</text><text x="134" y="403" class="m">segredos</text>
  <rect x="232" y="372" width="96" height="40" rx="5" class="g"/><text x="240" y="389" class="t">Semgrep</text><text x="240" y="403" class="m">SAST</text>
  <rect x="338" y="372" width="96" height="40" rx="5" class="g"/><text x="346" y="389" class="t">Terraform</text><text x="346" y="403" class="m">validate</text>
  <rect x="444" y="372" width="96" height="40" rx="5" class="g"/><text x="452" y="389" class="t">Trivy</text><text x="452" y="403" class="m">imagem</text>
  <rect x="550" y="372" width="118" height="40" rx="5" class="g"/><text x="558" y="389" class="t">Deploy (main)</text><text x="558" y="403" class="m">OIDC, sem senha</text>
  <text x="20" y="440" class="m">O Trivy reprova a imagem com HIGH ou CRITICAL corrigível. O deploy só roda se tudo passar.</text>
  <text x="20" y="455" class="m">Publica a imagem no ACR com o SHA do commit e atualiza o Container App.</text>

  <path d="M158 56 H214" class="l"/><path d="M158 96 H196 V84 H214" class="l"/><path d="M158 135 H190 V104 H214" class="l"/>
  <path d="M415 83 H469" class="l"/><path d="M315 124 V149" class="l" style="marker-end:none"/><path d="M415 190 H469" class="l" style="marker-end:none"/>
  <path d="M567 210 V229" class="l"/><path d="M715 56 H683" class="l"/><text x="688" y="50" class="m" text-anchor="start"></text>
</svg>
"""

HTML = """<!doctype html><html lang="pt-BR"><head><meta charset="utf-8"><title>Zela: Deploy Blindado (Secure DevOps &amp; Cloud Computing)</title>
<style>
@page { size: A4; margin: 14mm; }
body { font: 10.3pt/1.45 "Segoe UI", Roboto, Arial, sans-serif; color: #1c1b19; }
h1 { font-size: 21pt; margin: 0 0 4px; color: #0b5d4b; }
h2 { font-size: 13.5pt; color: #0b5d4b; border-bottom: 2px solid #0b5d4b; padding-bottom: 2px; margin: 18px 0 8px; break-after: avoid; }
h3 { font-size: 11pt; margin: 12px 0 4px; color: #0b5d4b; break-after: avoid; }
.sub { color: #55524c; margin: 0 0 10px; }
a { color: #0b5d4b; }
table { border-collapse: collapse; width: 100%; margin: 6px 0 10px; font-size: 9.2pt; break-inside: avoid; }
th, td { border: 1px solid #d6d2c8; padding: 4px 6px; text-align: left; vertical-align: top; }
th { background: #e3f1ec; }
.ok { color: #0b5d4b; font-weight: 700; } .pend { color: #a1121d; font-weight: 700; }
.nota { font-size: 9pt; color: #55524c; }
.aviso { border-left: 4px solid #d98a00; background: #fdf5e6; padding: 6px 10px; margin: 8px 0; font-size: 9.6pt; }
code { font: 8.6pt Consolas, "DejaVu Sans Mono", monospace; background: #f3f1ec; padding: 0 3px; }
pre { font: 8.4pt/1.35 Consolas, "DejaVu Sans Mono", monospace; background: #f3f1ec; padding: 6px 8px; white-space: pre-wrap; break-inside: avoid; }
img.print { width: 100%; border: 1px solid #d6d2c8; }
.quebra { break-before: page; }
svg { width: 100%; height: auto; }
</style></head><body>

<h1>Deploy Blindado</h1>
<p class="sub">Secure DevOps Tools &amp; Cloud Computing · Prof. Cleórbete Santos · GS 2026.2 CitizenTech</p>
<p><b>Zela: Zeladoria Urbana por Foto.</b> O cidadão envia uma foto e um local, confirma a categoria que a IA sugere e recebe um protocolo para acompanhar o relato.</p>
<table>
<tr><th>Integrantes</th><td>Pedro Henrique de Assunção Lima (RM552746) · Joseh Gabriel Trimboli Agra (RM553094)</td></tr>
<tr><th>MVP em URL pública</th><td><a href="{MVP}">{MVP}</a></td></tr>
<tr><th>Repositório público</th><td><a href="{REPO}">{REPO}</a></td></tr>
<tr><th>Dockerfile</th><td><a href="{BLOB}/api/Dockerfile">api/Dockerfile</a> · <a href="{BLOB}/docker-compose.yml">docker-compose.yml</a></td></tr>
<tr><th>Terraform</th><td><a href="{BLOB}/infra/terraform/main.tf">infra/terraform/</a></td></tr>
<tr><th>Workflow</th><td><a href="{BLOB}/.github/workflows/ci.yml">.github/workflows/ci.yml</a></td></tr>
<tr><th>Observabilidade</th><td><a href="{BLOB}/infra/monitoring/grafana/dashboards/zela.json">painel do Grafana</a> · <a href="{BLOB}/infra/monitoring/alerts.yml">regras do Prometheus</a></td></tr>
<tr><th>Documentos</th><td><a href="{BLOB}/docs/arquitetura.md">arquitetura</a> · <a href="{BLOB}/docs/custos_e_lgpd.md">custos e LGPD</a> · <a href="{BLOB}/infra/evidencias/README.md">evidências</a> · <a href="{BLOB}/docs/ficha_tecnica.md">ficha técnica</a></td></tr>
</table>

<div class="aviso"><b>Transparência sobre o pipeline.</b> Os runners hospedados do GitHub Actions estão bloqueados na conta do repositório por um problema de cobrança do GitHub ("account is locked due to a billing issue"). O pipeline roda num <b>runner próprio</b>, registrado no repositório e executado no computador do desenvolvedor. Na execução <a href="{REPO}/actions/runs/43093596676">43093596676</a> (commit 52c4321) os 6 jobs terminaram em sucesso, inclusive o deploy. A seção 9 lista as limitações conhecidas.</div>

<h2>1. Arquitetura</h2>
{DIAGRAMA}
<p class="nota">Código-fonte do diagrama em <a href="{BLOB}/docs/arquitetura.md">docs/arquitetura.md</a>. Toda a infraestrutura do Azure é criada por Terraform. O pipeline só publica a imagem.</p>

<h3>Fluxo de entrega</h3>
<ol>
<li>Um push na <code>main</code> dispara o workflow <code>ci</code>.</li>
<li>Rodam em paralelo: testes (pytest), Gitleaks (segredos no histórico), Semgrep (SAST de Python e Dockerfile) e <code>terraform validate</code>.</li>
<li>O Trivy varre a imagem e reprova o pipeline se houver vulnerabilidade HIGH ou CRITICAL com correção disponível.</li>
<li>Só se tudo passar, o job <code>deploy</code> entra no Azure por OIDC (sem senha guardada), publica a imagem no ACR com o SHA do commit, atualiza o Container App e confere o <code>/health</code>.</li>
</ol>

<h2>2. Container e infraestrutura como código</h2>
<table>
<tr><th>Critério</th><th>Como foi atendido</th></tr>
<tr><td>Dockerfile enxuto, usuário não root</td><td>Base <code>python:3.12-slim</code>, <code>--no-cache-dir</code>, usuário <code>zela</code> (uid 10001) e <code>HEALTHCHECK</code>. O YOLO é opcional (<code>COM_VISAO=1</code>) para a imagem não crescer ~1 GB sem necessidade.</td></tr>
<tr><td>Sem segredo na imagem</td><td>Tokens, senha do banco e <code>DATABASE_URL</code> chegam por variáveis de ambiente (<em>secrets</em> do Container App). O <code>.env</code> é ignorado pelo git e o Gitleaks varre o histórico.</td></tr>
<tr><td>Stack sobe com docker compose</td><td><code>docker compose up</code> sobe API e Postgres. <code>docker-compose.monitoring.yml</code> adiciona Prometheus e Grafana.</td></tr>
<tr><td>Nuvem criada por Terraform</td><td>14 recursos em <code>infra/terraform/</code>: resource group, ACR, Postgres, Log Analytics, ambiente e Container App, identidade gerenciada, alerta e grupo de ação. O <code>subscription_id</code> fica fixado no provider.</td></tr>
<tr><td>State e .tfvars fora do repositório</td><td><code>*.tfstate</code>, <code>*.tfvars</code>, <code>*.plan</code> e <code>.terraform/</code> estão no <code>.gitignore</code>. Só o <code>terraform.tfvars.example</code> vai ao git.</td></tr>
<tr><td>Porta administrativa nunca aberta para 0.0.0.0/0</td><td>Só a API é pública (HTTPS). O banco aceita apenas a regra "serviços do Azure" (início e fim 0.0.0.0, que não é a internet), com TLS e senha. Nenhuma porta de administração (SSH, 5432 aberta ao mundo) é exposta.</td></tr>
</table>

<h2>3. Pipeline DevSecOps</h2>
<p>Workflow: <a href="{BLOB}/.github/workflows/ci.yml">.github/workflows/ci.yml</a>, com 6 jobs: <code>testes</code>, <code>gitleaks</code>, <code>semgrep</code>, <code>terraform</code>, <code>imagem</code> (Trivy) e <code>deploy</code>. Roda a cada push e pull request, e o <code>deploy</code> só na <code>main</code>, depois de todos os outros. O runner é escolhido pela variável do repositório <code>RUNNER_LABEL</code> (hoje <code>zela-local</code>). O login no Azure é por OIDC, com os identificadores em GitHub Secrets (<code>AZURE_CLIENT_ID</code>, <code>AZURE_TENANT_ID</code>, <code>AZURE_SUBSCRIPTION_ID</code>) e sem senha guardada.</p>
<h3>Resultado no GitHub Actions</h3>
<p>Execução <a href="{REPO}/actions/runs/43093596676">43093596676</a>, commit <code>52c4321</code>, em runner próprio:</p>
<table>
<tr><th>Job</th><th>Ferramenta</th><th>Resultado</th></tr>
<tr><td>testes</td><td>pytest (dentro de <code>api/</code>)</td><td class="ok">sucesso (30 testes localmente)</td></tr>
<tr><td>gitleaks</td><td>Gitleaks 8.30.1, histórico git inteiro</td><td class="ok">sucesso, nenhum segredo</td></tr>
<tr><td>semgrep</td><td>Semgrep 1.97.0, regras <code>p/python</code> e <code>p/dockerfile</code></td><td class="ok">sucesso (158 regras, 0 achados localmente)</td></tr>
<tr><td>terraform</td><td><code>terraform validate</code> e <code>fmt</code></td><td class="ok">sucesso</td></tr>
<tr><td>imagem</td><td>Trivy 0.76.2, HIGH e CRITICAL com correção</td><td class="ok">sucesso (0 vulnerabilidades)</td></tr>
<tr><td>deploy</td><td>OIDC, build, push no ACR, atualização do Container App, teste de fumaça</td><td class="ok">sucesso: imagem <code>zela-api:52c4321e5445</code> no ar</td></tr>
</table>
<p class="nota">Até chegar aqui foram três execuções com falha, todas por defeitos do próprio workflow e não por achados de segurança: o <code>pytest</code> rodava fora de <code>api/</code>; a action do Gitleaks quebrava no envio do relatório e varria só 1 commit; a versão da action do Trivy não existia; e a credencial OIDC usava o formato antigo do <em>subject</em> (o GitHub agora inclui os IDs numéricos do dono e do repositório). Foram corrigidos com Gitleaks e Trivy por Docker e uma segunda credencial federada. Os testes, o Semgrep e o <code>terraform validate</code> também foram rodados localmente em 11/11/2026.</p>
<h3>Uma execução barrada e a corrigida</h3>
<p>A primeira varredura do Trivy <b>reprovou</b> a imagem (commit <a href="{REPO}/commit/0855ed2">0855ed2</a>) com 7 achados HIGH corrigíveis:</p>
<table>
<tr><th>Origem</th><th>Pacote</th><th>Correção</th></tr>
<tr><td>Sistema (Debian 13)</td><td><code>apt</code> e <code>libapt-pkg7.0</code> (CVE-2026-109518)</td><td><code>apt-get upgrade</code> no Dockerfile (apt 3.0.4)</td></tr>
<tr><td>Sistema (Debian 13)</td><td><code>zlib1g</code> (CVE-2026-76844, CVE-2026-85091)</td><td>zlib <code>1.3.dfsg+really1.3.1-1+deb13u1</code></td></tr>
<tr><td>Python</td><td><code>starlette</code> 0.46.2 (CVE-2025-62727, CVE-2026-48818, CVE-2026-54283)</td><td>FastAPI 0.162 e Starlette 1.3.1 ou superior (instalado: 1.10)</td></tr>
</table>
<p>O commit <a href="{REPO}/commit/c8fc16d">c8fc16d</a> corrigiu os 7 achados, e o Trivy passou a sair com código 0. Essa reprovação e a correção foram verificadas <b>localmente</b>, antes de o pipeline rodar no GitHub, então a evidência de "barrada e corrigida" não é uma execução do Actions. Saída das ferramentas em <a href="{BLOB}/infra/evidencias/README.md">infra/evidencias/</a>.</p>

<h2>4. Observabilidade</h2>
<p>O Prometheus lê o <code>/metrics</code> do MVP publicado no Azure e o Grafana mostra o painel <b>Zela: 4 sinais de ouro</b>. A imagem abaixo é do painel lendo a API em produção, com tráfego e erros provocados de propósito.</p>
<table>
<tr><th>Sinal</th><th>Consulta</th></tr>
<tr><td>Latência</td><td><code>histogram_quantile(0.95, sum(rate(zela_latencia_segundos_bucket[5m])) by (le))</code> (também p50)</td></tr>
<tr><td>Tráfego</td><td><code>sum(rate(zela_requisicoes_total[5m])) by (rota)</code></td></tr>
<tr><td>Erros</td><td>% de respostas <code>status=~"5.."</code> sobre o total</td></tr>
<tr><td>Saturação</td><td><code>rate(process_cpu_seconds_total[5m])</code> e <code>process_resident_memory_bytes</code></td></tr>
</table>
<img class="print" src="data:image/jpeg;base64,{GRAFANA}" alt="Painel do Grafana com os 4 sinais de ouro">
<h3>Alerta disparado</h3>
<p>O alerta <code>zela-erros-5xx</code> (Azure Monitor, consulta nos logs do contêiner) avisa por e-mail quando passa de 5 respostas 5xx em 5 minutos. Depois de 10 respostas 500 provocadas de propósito, ele entrou em <b>Fired</b> às <b>19:36 UTC de 11/11/2026</b> (gravidade Sev2). A prova está em <a href="{BLOB}/infra/evidencias/alerta_disparado.json">infra/evidencias/alerta_disparado.json</a>. Não foi verificado se o e-mail chegou à caixa de entrada.</p>
<p class="nota">Dois problemas foram achados e corrigidos no caminho: a métrica <code>Requests</code> do Container App não entrega a divisão por categoria de status, então o primeiro alerta (por métrica) nunca dispararia e foi trocado por consulta nos logs; e erros 500 não tratados não eram contados no <code>/metrics</code> da API, o que foi corrigido com teste automático.</p>

<h2>5. Responsabilidade compartilhada</h2>
<table>
<tr><th>Camada</th><th>Quem responde</th><th>O que a equipe faz</th></tr>
<tr><td>Datacenter, hardware e rede física</td><td>Microsoft</td><td>Escolher a região permitida pela assinatura (<code>spaincentral</code>)</td></tr>
<tr><td>Serviços gerenciados (Container Apps, Postgres, ACR, Log Analytics)</td><td>Microsoft: disponibilidade e patches do serviço</td><td>Configurar tamanho, backup de 7 dias e retenção de logs de 30 dias</td></tr>
<tr><td>Imagem e dependências</td><td><b>Equipe</b></td><td>Manter sem CVE alta (Trivy), usuário não-root, sem segredo na imagem</td></tr>
<tr><td>Código da aplicação</td><td><b>Equipe</b></td><td>Validar entradas, limitar uploads, remover EXIF, proteger rotas de triagem e do robô por token</td></tr>
<tr><td>Identidades e segredos</td><td><b>Equipe</b></td><td>Secrets do Container App e do GitHub, identidade gerenciada para o pull do ACR, OIDC no deploy, state e tfvars fora do git</td></tr>
<tr><td>Dados pessoais (LGPD)</td><td><b>Equipe</b> (controladora no piloto)</td><td>Minimizar, documentar e responder ao titular</td></tr>
<tr><td>Monitoramento e resposta</td><td><b>Equipe</b></td><td>Painel, alerta por e-mail e a decisão de agir</td></tr>
</table>

<h2>6. Dados pessoais (LGPD)</h2>
<p>Dados tratados: <b>foto</b> da via, <b>localização</b> (texto e coordenadas) e <b>descrição livre</b>. Ficam no PostgreSQL e no disco do contêiner, na região <code>spaincentral</code> (União Europeia, o que configura transferência internacional). O relato é <b>anônimo</b>: não coletamos nome, CPF, telefone nem e-mail. A foto tem o EXIF (GPS e modelo do aparelho) removido no upload. O OpenRouter recebe só as dúvidas de uso do FonteBot, nunca fotos ou relatos. Detalhes em <a href="{BLOB}/docs/custos_e_lgpd.md">docs/custos_e_lgpd.md</a>.</p>
<h3>Riscos conhecidos que ainda não foram tratados</h3>
<ul>
<li><b>Leitura pública da API:</b> a listagem de relatos, o relato por id e a foto não exigem login, porque o painel da demo as consome. Qualquer pessoa com a URL vê localizações e fotos.</li>
<li><b>Sem rota de exclusão nem prazo de retenção</b> definido para os relatos.</li>
<li><b>Fotos em disco efêmero:</b> somem a cada novo deploy do contêiner. Azure Files resolveria.</li>
<li><b>Texto livre</b> pode receber dados pessoais. <b>/metrics</b> é público (só contadores agregados).</li>
<li><b>Estado do Terraform local:</b> guarda a senha do banco. Em produção, usar backend remoto criptografado.</li>
</ul>

<h2>7. Custos</h2>
<table>
<tr><th>Recurso</th><th>Configuração</th></tr>
<tr><td>Container App</td><td>0,5 vCPU e 1 GiB, 1 a 2 réplicas, HTTPS público</td></tr>
<tr><td>PostgreSQL Flexible Server</td><td>Burstable B1ms, 32 GB, backup de 7 dias</td></tr>
<tr><td>Container Registry</td><td>Basic</td></tr>
<tr><td>Log Analytics e alerta</td><td>Retenção de 30 dias, 1 alerta e 1 grupo de ação</td></tr>
</table>
<p><b>Estimativa: entre US$ 30 e US$ 60 por mês</b> com o piloto ligado o tempo todo. É uma estimativa por preços públicos, não um valor medido; o saldo real está em Cost Management no portal do Azure. O crédito do Azure for Students (cerca de US$ 100) cobre o período. O ambiente fica no ar durante a correção (cerca de uma semana depois de 19/11) e só então é destruído com <code>terraform destroy</code>. Mais formas de reduzir o custo em <a href="{BLOB}/docs/custos_e_lgpd.md">docs/custos_e_lgpd.md</a>.</p>

<h2>8. Como reproduzir</h2>
<pre>git clone {REPO}.git &amp;&amp; cd zela
cp .env.example .env            # preencha tokens e senha
docker compose up --build       # API em http://localhost:8000

# Monitoramento contra o MVP publicado
PROM_CONFIG=prometheus-azure.yml docker compose -f docker-compose.monitoring.yml up prometheus grafana

# Nuvem (conta Azure for Students)
cd infra/terraform &amp;&amp; cp terraform.tfvars.example terraform.tfvars
terraform init &amp;&amp; terraform plan -out tf.plan &amp;&amp; terraform apply tf.plan</pre>
<p class="nota">README completo em <a href="{BLOB}/infra/README.md">infra/README.md</a>, com o passo a passo do deploy e da configuração do acesso OIDC.</p>

<h2>9. Limitações conhecidas</h2>
<h3>Pipeline e entrega</h3>
<ul>
<li><b>Sem runner hospedado do GitHub.</b> A cobrança da conta está bloqueada, então o pipeline depende de um runner no computador do desenvolvedor, que precisa estar ligado. Um runner próprio em repositório público é um risco (um pull request malicioso executaria código na máquina). Mitigação: PRs de contribuidores externos exigem aprovação manual, e o runner deve ser removido depois da correção.</li>
<li><b>"Barrada e corrigida" não é uma execução do Actions.</b> A reprovação do Trivy e a correção foram verificadas localmente.</li>
<li><b>O Terraform não é aplicado pelo pipeline.</b> O CI só roda <code>validate</code> e <code>fmt</code>; o <code>apply</code> é manual, e o state fica na máquina do desenvolvedor (com a senha do banco).</li>
<li><b>Escopo das verificações.</b> O <code>test_vision.py</code> fica fora do CI, o Trivy varre só vulnerabilidades (não configuração) e o Semgrep usa regras da comunidade. O teste de fumaça do deploy confere apenas o <code>/health</code>.</li>
<li><b>O deploy automático foi validado em uma execução.</b> O acesso OIDC tem papel Contributor restrito ao grupo de recursos do Zela.</li>
</ul>
<h3>Observabilidade</h3>
<ul>
<li><b>Prometheus e Grafana rodam localmente</b>, apontando para o MVP no Azure. Não há dashboard hospedado nem Application Insights, e as regras do Prometheus não notificam ninguém (não há Alertmanager). Quem avisa a equipe é o alerta do Azure Monitor.</li>
<li><b>O e-mail do alerta não foi confirmado.</b> O alerta entrou em <code>Fired</code>, mas não foi verificado se a mensagem chegou à caixa de entrada.</li>
<li>O Grafana local usa a senha padrão <code>admin</code>, adequada só para uso local.</li>
</ul>
<h3>Produto, dados e infraestrutura</h3>
<ul>
<li><b>Sem sugestão de dano pela IA em produção.</b> A imagem publicada roda sem o YOLO (o modelo ainda não foi treinado), então o relato não recebe a sugestão automática.</li>
<li><b>Leitura pública da API</b> (listagem, relato e foto), <b>sem rota de exclusão nem prazo de retenção</b>, e texto livre sem filtro de dados pessoais. Detalhes na seção 6.</li>
<li><b>Fotos em disco efêmero:</b> somem a cada novo deploy do contêiner.</li>
<li><b>Banco sem rede privada:</b> aceita apenas a regra "serviços do Azure", com TLS e senha. Para produção, o certo é rede virtual e endpoint privado. O <code>/metrics</code> também é público.</li>
<li><b>Região imposta pela assinatura:</b> <code>spaincentral</code> é uma das poucas permitidas, o que implica transferência internacional de dados.</li>
<li><b>Custo estimado, não medido</b> (US$ 30 a 60 por mês). O ambiente precisa ficar no ar durante a correção, e o crédito de estudante limita o orçamento.</li>
<li>Instância única e sem alta disponibilidade, adequada a um piloto.</li>
</ul>
</body></html>
"""

html = (HTML.replace("{DIAGRAMA}", DIAGRAMA).replace("{GRAFANA}", grafana)
        .replace("{MVP}", MVP).replace("{REPO}", REPO).replace("{BLOB}", BLOB))
saida_html = AQUI / "Zela_DevSecOps.html"
saida_html.write_text(html, encoding="utf-8")

chrome = next((c for c in ("google-chrome", "chromium", "chromium-browser", "chrome") if shutil.which(c)), None)
if not chrome:
    sys.exit(f"HTML gerado em {saida_html}. Instale o Chrome/Chromium ou imprima o HTML como PDF pelo navegador.")
with tempfile.TemporaryDirectory() as perfil:
    subprocess.run([chrome, "--headless=new", "--disable-gpu", "--no-first-run", f"--user-data-dir={perfil}",
                    "--no-pdf-header-footer", f"--print-to-pdf={AQUI / 'Zela_DevSecOps.pdf'}", saida_html.as_uri()],
                   check=True, capture_output=True, timeout=120)
print("PDF gerado:", AQUI / "Zela_DevSecOps.pdf")
