# Zela: zeladoria urbana por foto

> Nome provisório. Global Solution 2026.2 · CitizenTech · Engenharia de Software 4º ano · entrega de 9 a 19 de novembro de 2026.
>
> **MVP no ar:** https://ca-zela-uylmp.jollyglacier-50c67627.spaincentral.azurecontainerapps.io · **Repositório:** https://github.com/phz1n777/zela

Você fotografa o dano na via e confirma a sugestão do sistema. Depois, acompanha o encaminhamento da ocorrência.

O cidadão registra um buraco ou outro dano na pista com uma foto e a localização aproximada. A visão computacional sugere se há dano na pista e mostra a confiança dessa sugestão. A pessoa confirma ou corrige, e a ocorrência entra numa fila de manutenção com protocolo e status.

## Escopo do MVP

**Dentro**

- Território piloto: o bairro Jardim das Belezas, onde mora um dos integrantes. O piloto serve para validar o uso pelo cidadão; os primeiros compradores pagantes continuam sendo campus e parque empresarial.
- Uma categoria automática: **dano na pista** (buraco ou rachadura). As demais ocorrências podem ser registradas por categoria manual, sem detecção automática.
- Formulário curto e responsivo, sem exigir conta. A pessoa confirma a sugestão da visão.
- Painel de triagem com foto, local, categoria sugerida, confirmação humana e status.
- Encaminhamento por robô (UiPath) para uma fila de teste ou para um portal cuja viabilidade tenha sido comprovada.
- Dados simulados identificados como demonstração.

**Fora**

- Cobertura de toda a cidade, rotas ou previsão de alagamento.
- Detecção automática de lixo, bueiros ou calçadas.
- Promessa de reparo, prazo de atendimento ou despacho automático de equipe.
- Severidade confiável. A estimativa de tamanho do dano é só um indicativo para a triagem.
- Dependência da integração com o SP156 antes de provarmos que ela funciona.

A classificação apoia a triagem. Ela não substitui a avaliação humana nem determina se a via é segura.

## Ficha técnica comum

| Campo | Conteúdo |
| --- | --- |
| Nome do produto | Zela: Zeladoria Urbana por Foto (provisório) |
| Cidadão e território | Quem circula a pé, de bicicleta, de carro ou em cadeira de rodas pelo bairro Jardim das Belezas (território piloto) |
| Problema, em uma frase | Danos na via ficam sem relato claro porque as pessoas não sabem onde relatar, o que informar ou se o problema já foi encaminhado |
| Proposta de valor | Transformar uma foto e um local em uma ocorrência estruturada e acompanhável |
| Arquitetura: componentes | PWA · API FastAPI · Visão (YOLO) · SQLite/Postgres · Airflow · Robô UiPath · FonteBot (GenAI) · Placa QR (Maker Lab) · Docker, Terraform e GitHub Actions |
| Fontes de dados | Relatos enviados no piloto · fotos locais para avaliar o modelo · RDD2022 (CC BY 4.0) como ponto de partida do treino · registros simulados marcados como demonstração |
| Modelos de IA utilizados | YOLO11n ajustado no RDD2022 para dano na pista · LLM do FonteBot via OpenRouter (`nvidia/nemotron-3.5-super-vl:free`, com fallback) para dúvidas de uso |
| URL do MVP e repositório | https://ca-zela-uylmp.jollyglacier-50c67627.spaincentral.azurecontainerapps.io · https://github.com/phz1n777/zela |
| Indicadores de impacto | Relatos registrados no piloto · % de sugestões confirmadas pelo cidadão · tempo do relato ao encaminhamento · ocorrências por status |
| ODS conectados | 11 (cidades sustentáveis), 9 (infraestrutura) e 13 (clima), com a contribuição descrita de forma concreta |

## Limites declarados

- **Visão:** o RDD2022 tem 47.420 imagens de seis países e não cobre ruas brasileiras em particular. Avaliamos o modelo também com fotos do piloto, mas esse resultado não prova que ele generaliza.
- **RPA:** ainda não sabemos se o SP156 tem API ou se o UiPath consegue operar o portal. Faremos uma prova curta (fluxo autorizado, autenticação, campos, anexos e bloqueios). Se não der certo dentro do prazo, o robô usa um portal de demonstração e a limitação fica documentada.
- **Dados:** registros simulados ficam marcados como demonstração e não contêm nome, telefone, rosto nem placa.

## Onde cada disciplina entra

| Pasta | Disciplina | Situação |
| --- | --- | --- |
| [`api/`](api) | Base de todas | API no contrato comum (`reports`), com confirmação humana, triagem e testes |
| [`web/`](web) | Base / BI (demo do pitch) | App do cidadão (relato, confirmação e protocolo) e painel de triagem, servidos pela API |
| [`vision/`](vision) | Applied Computer Vision | Pronto para treinar no Colab. A API usa o modelo quando o `best.pt` existe. **Ainda sem o modelo treinado**: o MVP no ar roda sem a sugestão automática |
| [`zela-genai`](https://github.com/phz1n777/zela-genai) | Generative AI for Engineering | Repositório separado, só com o FonteBot: notebook executado, FAQ, README e evidências |
| [`data/`](data) | Big Data & Data Integration | DAG `zela_relatos` rodando no Airflow 2.10, com diagrama e dicionário de dados. A entrega oficial, com os prints do Airflow e o PDF, está no repositório do Joseh: https://github.com/Zoviskgabriel/BigData-Data-Zeladoria-Urbana-por-Foto |
| [`rpa/`](rpa) | Robotic Process Automation | Assessment, business case, BPMN As-Is e To-Be e especificação do robô. O pacote oficial (PDF, projeto UiPath com `.xaml` e vídeo) foi entregue à parte pelo Joseh. O robô opera o portal de demonstração dele, não o MVP no Azure |
| [`infra/`](infra) | Secure DevOps & Cloud | Em produção no Azure Container Apps (Terraform, Postgres, painel no Grafana e alerta de 5xx que disparou). Pipeline no GitHub Actions com Gitleaks, Semgrep, Trivy e deploy por OIDC: a execução [43093596676](https://github.com/phz1n777/zela/actions/runs/43093596676) passou nos 6 jobs, em runner próprio, porque os runners do GitHub estão bloqueados por cobrança. PDF da entrega em [docs/entrega_devsecops](docs/entrega_devsecops/Zela_DevSecOps.pdf), com as limitações conhecidas |
| [`maker/`](maker) | Project-Based Maker Lab | **Não iniciado.** Sem responsável. O enunciado pede o redesenho de um objeto real da cidade, com CAD, peças fabricadas e publicação no MakerWorld |
| [`docs/`](docs) | BI & Startup Development | Lean Canvas, modelo de negócio, roteiro de entrevistas, ficha técnica, roteiro do pitch e PDF da entrega. Falta o vídeo do pitch |

## Contrato de dados compartilhado

O Airflow e o UiPath consomem o mesmo `report_id` da aplicação e não mantêm cadastros paralelos.

Tabela `reports`:

| Campo | Tipo | Conteúdo |
| --- | --- | --- |
| `id` | inteiro | `report_id`, também usado como número de protocolo |
| `created_at` | data e hora (UTC) | Quando o relato foi enviado |
| `location` | texto (3 a 200) | Endereço aproximado ou ponto de referência |
| `latitude`, `longitude` | número, opcional | GPS do celular, quando houver |
| `description` | texto (até 500) | Descrição curta do cidadão |
| `image` | texto | Nome do arquivo gerado pela API (nunca o nome enviado) |
| `category` | `dano_na_pista` · `calcada` · `bueiro` · `lixo` · `iluminacao` · `outro` | Categoria final. Só `dano_na_pista` tem sugestão automática |
| `status` | `recebido` · `em_triagem` · `encaminhado` · `descartado` | Situação do relato (mesmos nomes da FAQ do FonteBot) |
| `source` | `cidadao` · `demo` | `demo` marca dados simulados |
| `cv_label` | `dano_na_pista` · `sem_deteccao` · nulo | Sugestão da visão. Nulo quando o modelo não está disponível |
| `cv_confidence` | 0 a 1, ou nulo | Maior confiança entre as detecções válidas |
| `cv_model` | texto ou nulo | Modelo que gerou a sugestão |
| `cv_reviewed` | booleano | Se o cidadão já confirmou ou corrigiu a categoria |
| `service_order` | texto ou nulo | Número da ordem de serviço gravado pelo robô |

O `confirm_token` também fica na tabela, mas só aparece na resposta da criação e nunca nas consultas.

Ciclo de vida:

1. O cidadão envia o relato (`recebido`). A API grava a sugestão da visão e devolve o `confirm_token`.
2. O cidadão confirma ou corrige a categoria uma vez (`cv_reviewed = true`).
3. A triagem passa o relato para `em_triagem` ou `descartado`.
4. O robô pega os relatos `em_triagem`, abre a ordem de serviço e grava o número (`encaminhado`).

## Como rodar

Com Docker:

```bash
cp .env.example .env   # depois troque a senha e gere o ROBO_TOKEN e o OPERADOR_TOKEN
docker compose up --build
```

O app do cidadão abre em http://localhost:8000, o painel em http://localhost:8000/painel.html e a documentação interativa da API em http://localhost:8000/docs.

Sem Docker, só a API, com SQLite:

```bash
cd api
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python -m pytest -q
.venv/bin/uvicorn app.main:app --reload
```

Dados de demonstração (`source = demo`) para o painel e a DAG:

```bash
cd api
.venv/bin/python -m app.demo --quantidade 40     # --apagar remove só os demo
```

## Endpoints

| Método | Rota | Quem usa |
| --- | --- | --- |
| `POST` | `/api/reports` | App: `photo`, `location`, `description` e, opcionais, `latitude`, `longitude` e `category`. Devolve o relato e o `confirm_token` |
| `POST` | `/api/reports/{id}/confirmation` | App: `{category, confirm_token}`. O cidadão confirma ou corrige a sugestão, uma única vez |
| `GET` | `/api/reports` | Painel, Airflow: filtros `status`, `category`, `source` e `limit` |
| `GET` | `/api/reports/{id}` | App: acompanha o status pelo número do protocolo |
| `GET` | `/api/reports/{id}/image` | Painel: foto do relato |
| `PATCH` | `/api/reports/{id}/status` | Triagem (cabeçalho `x-operador-token`): `em_triagem` ou `descartado` |
| `GET` | `/robo/reports?status=em_triagem` | Robô UiPath (cabeçalho `x-robo-token`) |
| `PATCH` | `/robo/reports/{id}/service-order` | Robô UiPath grava a ordem de serviço e o relato vira `encaminhado` |
| `GET` | `/`, `/painel.html` | App do cidadão e painel de triagem (pasta `web/`) |
| `GET`/`POST` | `/portal-demo/` | Portal de **demonstração** da fila de manutenção, alvo do robô UiPath. Exige `PORTAL_DEMO_USUARIO` e `PORTAL_DEMO_SENHA` |
| `GET` | `/health` | Healthcheck do container |
| `GET` | `/metrics` | Prometheus (latência, tráfego e erros) |

## Segurança, acessibilidade e LGPD

- Não coletamos nome, CPF nem telefone, só a foto, o local e a descrição. Pedimos para evitar rostos e placas nas fotos.
- As fotos são salvas com nome gerado pela API, com limite de 5 MB e só em JPEG, PNG ou WebP. O EXIF (GPS e modelo do aparelho) é removido no upload.
- As rotas do robô e da triagem exigem tokens diferentes. A confirmação de categoria exige o token devolvido só para quem enviou o relato. Os segredos ficam no `.env`, fora do git, e as portas administrativas não ficam expostas ao público.
- O container roda com usuário sem privilégios.
- Linguagem simples, bom contraste, navegação por teclado e uma lista como alternativa ao mapa.
