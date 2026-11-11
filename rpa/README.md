# rpa: Robotic Process Automation

O robô transforma um relato validado em ordem de serviço numa fila de manutenção, sempre com o mesmo `report_id` da aplicação.

| Entrega | Arquivo | Situação |
| --- | --- | --- |
| Assessment do processo | [assessment.md](assessment.md) | Pronto. A tabela da prova curta (seção 5) precisa ser preenchida |
| Business case | [business_case.md](business_case.md) | Pronto. Os tempos são **estimativas**: cronometrar e trocar |
| BPMN As-Is | [bpmn/as_is.bpmn](bpmn/as_is.bpmn) · [imagem](bpmn/as_is.png) | Pronto |
| BPMN To-Be | [bpmn/to_be.bpmn](bpmn/to_be.bpmn) · [imagem](bpmn/to_be.png) | Pronto |
| Especificação do robô e RPA x API | [especificacao_robo.md](especificacao_robo.md) | Pronto |
| Portal de demonstração (destino do robô) | [`/portal-demo/`](../api/app/portal_demo.py) | Pronto e testado. Login, formulário com anexo e número da OS em `#numero-os` |
| Automação `.xaml` | `ZelaEncaminhamento/` (projeto do Studio) | **A fazer no UiPath Studio**, seguindo a especificação |
| Vídeo de até 3 minutos | | A fazer |
| Pacote `.zip` | | A fazer: projeto do Studio + documentos + BPMN |

## BPMN

Os `.bpmn` abrem no [Camunda Modeler](https://camunda.com/download/modeler/), no [bpmn.io](https://demo.bpmn.io) e no Bizagi Modeler. Os dois foram importados no bpmn.io sem nenhum aviso. Eles são gerados por [bpmn/gerar_bpmn.py](bpmn/gerar_bpmn.py): para mudar um fluxo, edite as listas do script e rode `python3 gerar_bpmn.py`. Se ajustarem à mão no Modeler, deixem de usar o script, senão as mudanças se perdem.

## Endpoints usados pelo robô

| Método | Rota | Cabeçalho |
| --- | --- | --- |
| `GET` | `/robo/reports?status=em_triagem` | `x-robo-token` |
| `GET` | `/api/reports/{id}/image` | (público) |
| `PATCH` | `/robo/reports/{id}/service-order` com `{"service_order": "..."}` | `x-robo-token` |

## Prova curta antes de investir

Não partimos do princípio de que o SP156 não tem API, nem de que o UiPath consegue operar o portal. As perguntas e a regra de decisão estão na seção 5 do [assessment](assessment.md). Se não for viável no prazo, o robô opera o **portal de demonstração** em `/portal-demo/`, que já está pronto, e a limitação fica declarada. Credenciais ficam em Assets do Orchestrator ou no Windows Credential Manager, nunca no repositório.
