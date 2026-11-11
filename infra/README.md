# infra: Secure DevOps & Cloud

Dockerfile em `api/` (usuário não-root). Nuvem: **Azure Container Apps + PostgreSQL Flexible Server + ACR**, descrita em `terraform/`.

## Arquivos

| Caminho | O que é |
| --- | --- |
| `terraform/` | Resource group, ACR, Postgres B1ms, Container App (HTTPS público), Log Analytics, alerta de 5xx por e-mail |
| `monitoring/` + `../docker-compose.monitoring.yml` | Prometheus lendo `/metrics`, com alertas `ZelaErros5xx` e `ZelaLatenciaAlta` (uso local) |
| `../.github/workflows/ci.yml` | Testes, Gitleaks, Semgrep, `terraform validate` e Trivy na imagem |

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
- **Custo e LGPD**: ver [`docs/custos_e_lgpd.md`](../docs/custos_e_lgpd.md). Estimativa de US$ 30 a 60 por mês; `terraform destroy` após a entrega.
