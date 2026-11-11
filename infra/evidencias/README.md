# Evidências do pipeline de segurança

As ferramentas de segurança foram executadas em 2026-11-11, na máquina do desenvolvedor, com as mesmas verificações do workflow [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml).

**Por que local:** o GitHub Actions da conta do repositório ficou bloqueado por cobrança ("account is locked due to a billing issue"), então os jobs não chegaram a executar. O workflow permanece no repositório e roda assim que o bloqueio for resolvido.

| Job do CI | Ferramenta | Resultado | Arquivo |
| --- | --- | --- | --- |
| `gitleaks` | Gitleaks (histórico git inteiro) | Nenhum segredo (a contagem de commits está no arquivo) | [gitleaks.txt](gitleaks.txt) |
| `semgrep` | Semgrep 1.97.0, regras `p/python` e `p/dockerfile` | 158 regras, 0 achados | [semgrep.txt](semgrep.txt) |
| `imagem` | Trivy, HIGH e CRITICAL com correção disponível | 0 vulnerabilidades, saída 0 | [trivy.txt](trivy.txt) |
| `testes` | pytest | testes passando (contagem e versões no arquivo) | [testes.txt](testes.txt) |
| `terraform` | `terraform validate` | configuração válida | [terraform_validate.txt](terraform_validate.txt) |

## Execução no GitHub Actions (runner próprio)

Execução [43093596676](https://github.com/phz1n777/zela/actions/runs/43093596676), commit `52c4321`: os 6 jobs (`testes`, `gitleaks`, `semgrep`, `terraform`, `imagem` e `deploy`) terminaram em sucesso, e o Container App passou a rodar `zela-api:52c4321e5445`. O runner é próprio porque os runners hospedados da conta estão bloqueados por cobrança. Execuções anteriores falharam por defeitos do workflow, corrigidos no caminho.

## Observabilidade e alerta (em produção)

| Evidência | O que mostra | Arquivo |
| --- | --- | --- |
| Painel do Grafana "Zela: 4 sinais de ouro" | Latência (p50 e p95), tráfego por rota, erros (% de 5xx) e saturação (CPU e memória), lidos pelo Prometheus no MVP publicado no Azure | [grafana_4_sinais.jpg](grafana_4_sinais.jpg) |
| Alerta de 5xx disparado | O alerta `zela-erros-5xx` (Azure Monitor, consulta nos logs) entrou em `Fired` depois de 10 respostas 500 provocadas de propósito, e avisa por e-mail | [alerta_disparado.json](alerta_disparado.json) |

O primeiro alerta, por métrica, nunca disparou porque a métrica `Requests` do Container App não entrega a divisão por categoria de status. Foi trocado por uma consulta nos logs. Também foi corrigido um defeito que escondia erros: exceções não tratadas não eram contadas nas métricas do Prometheus.

## Correção feita a partir do Trivy

A primeira execução do Trivy reprovou a imagem (7 achados HIGH). Foram corrigidos em `api/Dockerfile` (`apt-get upgrade`, para `apt` e `zlib`) e em `api/requirements.txt` (`fastapi` 0.162 e `starlette` 1.3.1 ou superior). A imagem corrigida está publicada no ACR como `zela-api:v2` e em execução no Azure Container Apps.

## Como repetir

```bash
docker run --rm -v "$PWD:/repo" zricethezav/gitleaks:latest detect --source /repo --redact
docker run --rm -v "$PWD:/src" -w /src semgrep/semgrep:1.97.0 semgrep scan --config p/python --config p/dockerfile --error api infra
docker build -f api/Dockerfile -t zela-api:ci . && docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy:latest image --severity CRITICAL,HIGH --ignore-unfixed --exit-code 1 zela-api:ci
```
