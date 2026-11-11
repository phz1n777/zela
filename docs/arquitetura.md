# Arquitetura de produção e responsabilidade compartilhada

Documento da disciplina de Secure DevOps & Cloud. O texto explica o que roda onde, como o código chega à produção e quem responde por cada camada.

## Diagrama

```mermaid
flowchart LR
  subgraph Cidadao["Cidadão"]
    PWA["App web (PWA)<br/>foto, local, confirmação"]
  end
  subgraph Equipe["Equipe"]
    TRI["Painel de triagem"]
    RPA["Robô UiPath"]
  end
  subgraph Dev["Desenvolvimento"]
    GIT["GitHub (repositório público)"]
    CI["GitHub Actions<br/>testes · Gitleaks · Semgrep<br/>Terraform validate · Trivy"]
  end
  subgraph Azure["Azure (spaincentral)"]
    ACR["Container Registry"]
    CA["Container App (HTTPS)<br/>API FastAPI + web<br/>usuário não-root"]
    PG[("PostgreSQL 16<br/>Flexible Server")]
    LA["Log Analytics"]
    AL["Alerta de 5xx<br/>(consulta nos logs)"]
  end
  subgraph Obs["Observabilidade (local)"]
    PROM["Prometheus"]
    GRAF["Grafana<br/>4 sinais de ouro"]
  end

  PWA -->|HTTPS| CA
  TRI -->|HTTPS + token operador| CA
  RPA -->|token do robô| CA
  CA -->|TLS, senha| PG
  CA -->|logs de console| LA
  LA --> AL -->|e-mail| EQ["Equipe"]
  PROM -->|"scrape /metrics"| CA
  PROM --> GRAF
  GIT --> CI -->|"build, push (OIDC)"| ACR
  CI -->|"az containerapp update"| CA
  ACR -->|"pull (identidade gerenciada)"| CA
```

A infraestrutura inteira é criada por Terraform (`infra/terraform/`). O pipeline só publica a imagem; ele não altera a infraestrutura.

## Fluxo de entrega

1. Um push na `main` dispara o workflow `ci`.
2. Rodam em paralelo: testes (pytest), Gitleaks (segredos no histórico), Semgrep (análise estática de Python e Dockerfile) e `terraform validate`.
3. Depois dos testes, o Trivy varre a imagem e **reprova** o pipeline se houver vulnerabilidade HIGH ou CRITICAL com correção disponível.
4. Só se tudo passar, o job `deploy` faz login no Azure por OIDC (sem senha guardada), publica a imagem no ACR com o SHA do commit e atualiza o Container App. Um teste de fumaça confere o `/health`.

## Responsabilidade compartilhada

| Camada | Quem responde | O que a equipe faz |
| --- | --- | --- |
| Datacenter, hardware, rede física, hipervisor | Microsoft | Nada. Escolher a região (`spaincentral`) por política da assinatura |
| Plataforma gerenciada (Container Apps, PostgreSQL Flexible Server, ACR, Log Analytics) | Microsoft: disponibilidade, patches do serviço, backups automáticos | Configurar: tamanho, retenção de backup (7 dias), retenção de logs (30 dias) |
| Imagem de contêiner e dependências | **Equipe** | Manter a base e as bibliotecas sem CVE alta (Trivy no pipeline), usuário não-root, sem segredo na imagem |
| Código da aplicação | **Equipe** | Validar entradas, limitar uploads, remover EXIF das fotos, proteger rotas de triagem e do robô por token |
| Identidades e segredos | **Equipe** | Segredos em *secrets* do Container App e do GitHub, `*.tfvars` e state fora do git, identidade gerenciada para o pull do ACR, OIDC no deploy |
| Rede e exposição | Compartilhada | Só a API é pública (HTTPS). O banco aceita apenas serviços do Azure, com senha e TLS. Nenhuma porta administrativa aberta para `0.0.0.0/0` |
| Dados pessoais (LGPD) | **Equipe** (controladora no piloto) | Minimizar, documentar e responder ao titular. Ver [custos_e_lgpd.md](custos_e_lgpd.md) |
| Monitoramento e resposta a incidentes | **Equipe** | Dashboard dos 4 sinais de ouro, alerta de 5xx por e-mail, e a decisão do que fazer ao ser acionada |

## Onde ficam os dados pessoais

Foto (sem EXIF), localização e descrição do relato ficam no PostgreSQL e no disco do contêiner, na região `spaincentral`. O relato é anônimo (sem nome, CPF, telefone ou e-mail). Detalhes, riscos e pendências em [custos_e_lgpd.md](custos_e_lgpd.md).
