# Evidências do pipeline de segurança

Executadas em 2026-11-11, na máquina do desenvolvedor, com as mesmas ferramentas e verificações do workflow [`.github/workflows/ci.yml`](../../.github/workflows/ci.yml).

**Por que local:** o GitHub Actions da conta do repositório ficou bloqueado por cobrança ("account is locked due to a billing issue"), então os jobs não chegaram a executar. O workflow permanece no repositório e roda assim que o bloqueio for resolvido.

| Job do CI | Ferramenta | Resultado | Arquivo |
| --- | --- | --- | --- |
| `gitleaks` | Gitleaks (histórico git inteiro) | 3 commits, nenhum segredo | [gitleaks.txt](gitleaks.txt) |
| `semgrep` | Semgrep 1.97.0, regras `p/python` e `p/dockerfile` | 158 regras, 0 achados | [semgrep.txt](semgrep.txt) |
| `imagem` | Trivy, HIGH e CRITICAL com correção disponível | 0 vulnerabilidades, saída 0 | [trivy.txt](trivy.txt) |
| `testes` | pytest | 25 testes passando | [testes.txt](testes.txt) |
| `terraform` | `terraform validate` | configuração válida | [terraform_validate.txt](terraform_validate.txt) |

## Correção feita a partir do Trivy

A primeira execução do Trivy reprovou a imagem (7 achados HIGH). Foram corrigidos em `api/Dockerfile` (`apt-get upgrade`, para `apt` e `zlib`) e em `api/requirements.txt` (`fastapi` 0.162 e `starlette` 1.3.1 ou superior). A imagem corrigida está publicada no ACR como `zela-api:v2` e em execução no Azure Container Apps.

## Como repetir

```bash
docker run --rm -v "$PWD:/repo" zricethezav/gitleaks:latest detect --source /repo --redact
docker run --rm -v "$PWD:/src" -w /src semgrep/semgrep:1.97.0 semgrep scan --config p/python --config p/dockerfile --error api infra
docker build -f api/Dockerfile -t zela-api:ci . && docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy:latest image --severity CRITICAL,HIGH --ignore-unfixed --exit-code 1 zela-api:ci
```
