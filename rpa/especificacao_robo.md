# Especificação do robô UiPath (para montar o `.xaml`)

Guia para construir o robô no UiPath Studio. O `.xaml` precisa ser montado e testado no Studio, então ele **não** foi gerado aqui. Esta especificação segue o To-Be de [bpmn/to_be.bpmn](bpmn/to_be.bpmn).

## Projeto

- **Nome:** `ZelaEncaminhamento` · **Tipo:** Process · **Framework:** Windows. Pode ser REFramework, se quiserem a estrutura de fila, retry e log já pronta.
- **Pacotes:** `UiPath.WebAPI.Activities` (HTTP Request e Deserialize JSON), `UiPath.UIAutomation.Activities`, `UiPath.System.Activities`.
- **Agendamento:** a cada 15 minutos (trigger do Orchestrator ou Agendador do Windows).

## Configuração (nunca no código)

| Nome | Onde guardar | Exemplo |
| --- | --- | --- |
| `ZelaApiUrl` | Asset do Orchestrator ou `Config.xlsx` | `https://<url-do-mvp>` |
| `ZelaRoboToken` | **Asset do tipo Credential** ou Windows Credential Manager | valor do `ROBO_TOKEN` |
| `PortalUrl` | Asset ou `Config.xlsx` | `{ZelaApiUrl}/portal-demo/` (portal de demonstração) ou a URL do portal real |
| `PortalCredencial` | **Asset do tipo Credential** | usuário e senha da conta da equipe |

`Config.xlsx` só pode ter valores não secretos. Tokens e senhas, nunca.

## Fluxo principal (`Main.xaml`)

1. **Ler a fila**
   - `HTTP Request` GET `{ZelaApiUrl}/robo/reports?status=em_triagem`, com o cabeçalho `x-robo-token: {ZelaRoboToken}`.
   - Se o status for diferente de 200: `Log Message` (Error) e encerrar. Um 401 indica token errado.
   - `Deserialize JSON Array` → `relatos`.
2. **Abrir o portal uma vez**: `Use Application/Browser` em `{PortalUrl}`, login com `Get Credential` e `Type Secure Text` na senha.
3. **`For Each relato in relatos`**, cada item dentro de **`Try Catch`**:
   1. `HTTP Request` GET `{ZelaApiUrl}/api/reports/{id}/image` → salvar em `%TEMP%\zela_{id}.jpg`.
   2. Preencher o formulário:
      - **Endereço** (`#endereco`) ← `location`
      - **Tipo** (`#tipo`) ← de-para da categoria (tabela abaixo)
      - **Descrição** (`#descricao`) ← `"Relato Zela nº " + id + ": " + description`
      - **Referência externa** (`#referencia`) ← `id`, que é o mesmo `report_id`
      - **Anexo** (`#anexo`) ← arquivo baixado
   3. `Click` em `#enviar`. Em seguida, `Check App State` esperando `#numero-os` aparecer e `Get Text` de `#numero-os`. Se aparecer `#erro-ordem`, leia o texto e trate como exceção do relato.
   4. `HTTP Request` PATCH `{ZelaApiUrl}/robo/reports/{id}/service-order`, corpo `{"service_order": "<número>"}`, mesmo cabeçalho.
      - **200**: `Log Message` Info "relato {id} encaminhado como {número}".
      - **409**: outro processo já encaminhou o relato. Registrar Warn e seguir.
   5. `Delete File` da foto temporária.
   - **Catch:** `Take Screenshot` + `Log Message` Error com o `id` e a mensagem. O relato **continua em `em_triagem`** e volta na próxima execução. Depois de 3 falhas no mesmo `id` (contador em log ou fila), avisar a equipe.
4. **Encerrar:** logout no portal e fechar o navegador.

## Portal de demonstração (`/portal-demo/`)

É o destino do robô enquanto o portal oficial não for viável. Ele é servido pela própria API do Zela, mas funciona como outro sistema, sem API: login, formulário HTML, anexo e tela de confirmação. Só fica ativo se `PORTAL_DEMO_USUARIO` e `PORTAL_DEMO_SENHA` estiverem definidos no servidor.

| Tela | URL | Seletores estáveis (`id`) |
| --- | --- | --- |
| Login | `/portal-demo/` | `#usuario`, `#senha`, `#entrar`. Erro em `#erro-login` |
| Nova ordem | `/portal-demo/nova` | `#endereco`, `#tipo` (select), `#descricao`, `#referencia`, `#anexo` (file), `#enviar`. Erro em `#erro-ordem` |
| Confirmação | `/portal-demo/ordens/{n}` | **`#numero-os`** (ex.: `OS-2026-000001`), `#os-referencia`, `#nova-ordem` |
| Lista | `/portal-demo/ordens` | `#lista-ordens` |
| Sair | botão no topo | `#sair` |

No UiPath, use seletores com `id` (por exemplo `<webctrl id='numero-os' />`), não posição na tela. Para o anexo, use `Set Text` ou `Type Into` no `#anexo` com o caminho do arquivo, ou a atividade `Upload File` do navegador.

## De-para de categoria

| `category` (Zela) | `#tipo` no portal demo (value) | Texto exibido |
| --- | --- | --- |
| `dano_na_pista` | `buraco_pavimento` | Buraco / pavimento |
| `calcada` | `calcada` | Calçada |
| `bueiro` | `drenagem` | Boca de lobo / drenagem |
| `lixo` | `limpeza` | Limpeza / entulho |
| `iluminacao` | `iluminacao` | Iluminação pública |
| `outro` | `outros` | Outros |

No portal real, ajuste a coluna do meio depois da prova curta.

## Teste antes de gravar o vídeo

Com a API local rodando (ver [web/README.md](../web/README.md)):

```bash
cd api && .venv/bin/python -m app.demo --quantidade 5
```

Depois, no painel `/painel.html`, coloque 2 relatos em triagem e rode o robô contra `http://localhost:8000/portal-demo/`. Os relatos precisam aparecer como "Encaminhado", com o número da ordem de serviço.

## RPA x API

| Critério | RPA (este robô) | API |
| --- | --- | --- |
| Pré-requisito | Só a interface do portal | O portal precisa ter API e autorizar o acesso |
| Tempo para construir | Baixo (Studio, gravador, seletores) | Médio (autenticação, contrato, testes) |
| Estabilidade | Quebra se o layout mudar | Estável enquanto o contrato da API não mudar |
| Infraestrutura | Máquina com o robô e licença | Nenhuma extra: roda dentro da API do Zela |
| Rastreabilidade | Logs e screenshots do robô | Logs da API |
| Quando escolher | Portal sem API, ou durante uma prova de conceito | Sempre que existir API autorizada |

No Zela, a parte do **nosso** lado já é API (`/robo/reports`). O RPA cobre só o lado do portal de destino. Se a prova curta encontrar uma API autorizada, trocar o robô por uma chamada direta na API do Zela é uma mudança pequena.
