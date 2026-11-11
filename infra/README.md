# infra: Secure DevOps & Cloud

Dockerfile em `api/` (usuário não-root). Nuvem: **Azure Container Apps + PostgreSQL Flexible Server + ACR**, descrita em `terraform/`.

## Arquivos

| Caminho | O que é |
| --- | --- |
| `terraform/` | Resource group, ACR, Postgres B1ms, Container App (HTTPS público), Log Analytics, alerta de 5xx por e-mail (consulta nos logs) |
| `monitoring/` + `../docker-compose.monitoring.yml` | Prometheus e Grafana locais (painel "Zela: 4 sinais de ouro"), contra a stack local ou o MVP no Azure. Alertas `ZelaErros5xx` e `ZelaLatenciaAlta` |
| `../.github/workflows/ci.yml` | Testes, Gitleaks, Semgrep, `terraform validate`, Trivy na imagem e deploy automático na `main` |
| `evidencias/` | Saída das ferramentas de segurança rodadas localmente |
| [`../docs/arquitetura.md`](../docs/arquitetura.md) | Diagrama, fluxo de entrega e responsabilidade compartilhada |

## Perfil Azure da faculdade

```bash
alias az-fiap='AZURE_CONFIG_DIR=$HOME/.azure-fiap az'
export AZURE_CONFIG_DIR=$HOME/.azure-fiap   # no terminal do Terraform
az account show                              # conferir: Azure for Students
```

O `subscription_id` fica fixado no provider, então um login na conta errada falha em vez de aplicar lá.

## Deploy

```bash
cd infra/terraform
cp terraform.tfvars.example terraform.tfvars   # preencher (fora do git)
terraform init && terraform plan -out tf.plan
terraform apply tf.plan                         # primeiro apply sobe uma imagem de teste

ACR=$(terraform output -raw acr_login_server)
az acr login --name "${ACR%%.*}"
docker build -f ../../api/Dockerfile -t $ACR/zela-api:latest ../..
docker push $ACR/zela-api:latest
# colocar imagem = "$ACR/zela-api:latest" no tfvars e aplicar de novo
```

## Decisões e riscos

- **Segredos**: tokens e senha do banco vão para secrets do Container App; state e `.tfvars` ficam fora do git.
- **Banco**: o acesso público fica restrito à regra "serviços do Azure" (0.0.0.0 a 0.0.0.0, não é a internet), com senha e TLS. Nenhuma porta administrativa aberta para `0.0.0.0/0`. Melhoria futura: VNet e endpoint privado.
- **Fotos**: o disco do Container App é efêmero, então as fotos somem a cada nova revisão. Para o piloto, montar Azure Files.
- **`/metrics` público**: expõe contadores agregados, sem dados pessoais. Restringir antes de produção.
- **Custo e LGPD**: ver [`docs/custos_e_lgpd.md`](../docs/custos_e_lgpd.md). Estimativa de US$ 30 a 60 por mês; `terraform destroy` só depois da correção (até cerca de 26/11), pois os links precisam funcionar durante ela.

## Observabilidade

```bash
# Contra o MVP publicado no Azure (não precisa subir a API local)
PROM_CONFIG=prometheus-azure.yml docker compose -f docker-compose.monitoring.yml up prometheus grafana
```

Grafana em http://localhost:3000 (usuário `admin`, senha `admin` só para uso local) com o painel **Zela: 4 sinais de ouro**: latência (p50 e p95), tráfego, erros (% de 5xx) e saturação (CPU e memória). O alerta em produção é do Azure Monitor: uma consulta nos logs do Container App que avisa por e-mail quando passa de 5 respostas 5xx em 5 minutos.

## Deploy automático (uma vez, para ligar o job `deploy`)

O job `deploy` do workflow entra no Azure por OIDC, sem guardar senha. Precisa de um registro de aplicativo com credencial federada ao repositório e de 3 *secrets* no GitHub. Use sempre o perfil da faculdade (`AZURE_CONFIG_DIR=$HOME/.azure-fiap`):

```bash
APP=$(az ad app create --display-name zela-github-deploy --query appId -o tsv)
az ad sp create --id "$APP"
SUB=$(az account show --query id -o tsv)
az role assignment create --assignee "$APP" --role Contributor \
  --scope "/subscriptions/$SUB/resourceGroups/rg-zela-uylmp"
az ad app federated-credential create --id "$APP" --parameters '{
  "name": "github-main", "issuer": "https://token.actions.githubusercontent.com",
  "subject": "repo:phz1n777/zela:ref:refs/heads/main", "audiences": ["api://AzureADTokenExchange"]}'
```

Depois, em *Settings → Secrets and variables → Actions* do repositório, crie `AZURE_CLIENT_ID` (o `$APP`), `AZURE_TENANT_ID` (`az account show --query tenantId`) e `AZURE_SUBSCRIPTION_ID`. O GitHub assina o login com o *subject* no formato novo, que inclui os IDs numéricos do dono e do repositório (`repo:<dono>@<id>/<repo>@<id>:ref:refs/heads/main`). Crie também uma segunda credencial federada com esse subject (o erro `AADSTS700213` mostra o valor exato). O papel fica restrito ao grupo de recursos do Zela. Em assinaturas de estudante, o locatário pode bloquear o registro de aplicativos; nesse caso o deploy continua manual (seção Deploy acima).

O Terraform ignora a imagem do Container App (`ignore_changes`), para não reverter o que o pipeline publicar.

## Runner próprio (quando o Actions hospedado não está disponível)

Se a conta estiver bloqueada por cobrança, os jobs podem rodar num runner registrado no repositório. Em *Settings → Actions → Runners → New self-hosted runner* o GitHub gera o token de registro; depois `./config.sh --url <repo> --token <token> --labels zela-local` e `./run.sh` (deixe em primeiro plano para poder parar com Ctrl-C). Crie a variável do repositório `RUNNER_LABEL=zela-local`; sem ela o workflow volta ao runner do GitHub.

Cuidados: em repositório público, exija aprovação para PRs de contribuidores externos (*Settings → Actions → General → Fork pull request workflows*); mantenha o runner ligado só enquanto precisar e remova-o depois. O runner precisa de Docker e do Azure CLI. Limitações conhecidas do projeto em [`docs/entrega_devsecops`](../docs/entrega_devsecops/Zela_DevSecOps.pdf), seção 9.
