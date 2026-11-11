# Assessment do processo: encaminhar relato validado como ordem de serviço

## 1. Processo avaliado

**Nome:** abertura de ordem de serviço a partir de um relato de dano na via.

**Gatilho:** um relato do Zela passa para `em_triagem`, ou seja, a equipe conferiu foto, local e categoria.

**Resultado esperado:** uma ordem de serviço aberta na fila de manutenção, com o número gravado de volta no relato (`service_order`) e o status `encaminhado`.

## 2. Como é feito hoje (As-Is)

Sem o robô, a mesma pessoa da triagem faz tudo à mão. O fluxo está em [bpmn/as_is.bpmn](bpmn/as_is.bpmn).

1. Abre o painel do Zela e escolhe um relato em triagem.
2. Abre o portal da fila de manutenção (ou o canal oficial) em outra aba e faz login.
3. Copia campo a campo: local, categoria, descrição, e baixa e anexa a foto.
4. Envia o formulário e copia o número da ordem de serviço.
5. Volta ao Zela e registra o número. Hoje não existe tela para isso, então vira uma anotação à parte.
6. Repete para o próximo relato.

## 3. Critérios de adequação ao RPA

| Critério | Avaliação | Nota (1 a 5) |
| --- | --- | --- |
| **Baseado em regras** | Sim. Mapeamento fixo de campos, sem decisão subjetiva. A decisão humana (validar o relato) acontece **antes**, na triagem | 5 |
| **Entrada digital e estruturada** | Sim. JSON da API (`GET /robo/reports`) | 5 |
| **Repetitivo e com volume** | Repetitivo, sim. O volume no piloto é **baixo** e ainda desconhecido, a medir | 3 |
| **Sistema de destino sem API** | **A confirmar** na prova curta. Se o destino tiver API, a integração por API é melhor (ver o [business case](business_case.md)) | ? |
| **Propenso a erro manual** | Sim. Copiar o local, a categoria e o número entre abas gera erro de digitação e relato sem número | 4 |
| **Processo estável** | O Zela é estável (contrato `reports`). O portal de destino pode mudar de layout, que é o risco clássico de RPA | 3 |
| **Exceções previsíveis** | Login expirado, campo obrigatório vazio, portal fora do ar, anexo recusado | 4 |

**Conclusão:** o processo é **candidato a RPA** desde que o destino não ofereça API. A decisão final depende da prova curta (seção 5).

## 4. Dados que o robô usa

| Origem (Zela) | Destino (portal) | Observação |
| --- | --- | --- |
| `id` | Referência externa / observação | Garante rastreio pelo mesmo `report_id` |
| `location` | Endereço / ponto de referência | Texto livre |
| `latitude`, `longitude` | Coordenadas (se o portal aceitar) | Opcionais |
| `category` | Tipo de serviço | Tabela de-para: `dano_na_pista` → "Buraco / pavimento", e assim por diante |
| `description` | Descrição | Prefixo "Relato Zela nº {id}:" |
| Foto (`GET /api/reports/{id}/image`) | Anexo | Baixada para pasta temporária e apagada depois |
| (retorno) número da OS | `PATCH /robo/reports/{id}/service-order` | Status vira `encaminhado` |

Dados pessoais: **nenhum**. O Zela não coleta nome, telefone nem e-mail. A conta do portal é da equipe, e não do cidadão.

## 5. Prova curta de viabilidade (antes de investir)

| Pergunta | Como verificar | Resultado |
| --- | --- | --- |
| Existe fluxo autorizado para abrir solicitações em nome da equipe? | Termos de uso do portal e contato com o responsável | *(preencher)* |
| Como é a autenticação? (gov.br, usuário e senha, 2FA) | Teste manual com conta da equipe | *(preencher)* |
| Quais campos e anexos são obrigatórios? | Abrir uma solicitação de teste manualmente | *(preencher)* |
| Há CAPTCHA, limite de envio ou outro bloqueio a automação? | Teste manual | *(preencher)* |
| Existe API pública ou integração oficial? | Documentação e dados abertos do órgão | *(preencher)* |

**Regra de decisão:**
- Se houver **CAPTCHA**, falta de autorização ou risco de ferir os termos, **não automatizamos o portal oficial**. Isso inclui o SP156 se for o caso. O robô passa a operar o **portal de demonstração** da fila de manutenção, e a limitação fica declarada.
- Se houver **API**, comparamos no business case. A API tende a ganhar em custo e estabilidade.
- Credenciais ficam no Orchestrator (Assets) ou no Windows Credential Manager. **Nunca** no `.xaml` nem no repositório.

## 6. Riscos

| Risco | Mitigação |
| --- | --- |
| Mudança de layout do portal | Seletores por atributos estáveis (id/name), screenshot e log em cada falha, relato continua em `em_triagem` para nova tentativa |
| Envio duplicado | O robô só lê `em_triagem`, e a API recusa (409) gravar OS em relato que não está em triagem |
| Portal fora do ar | Retry com espera. Após 3 falhas, o relato fica para a próxima execução e um alerta vai no log |
| Credencial vazada | Assets do Orchestrator, rotação do `ROBO_TOKEN`, token separado do operador |
| Automação sem autorização | Prova curta e decisão documentada antes de rodar no portal real |
