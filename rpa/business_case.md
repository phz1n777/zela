# Business case: robô de encaminhamento do Zela

> Os tempos abaixo são **estimativas a medir**. Cronometrem 5 encaminhamentos manuais e 5 do robô e troquem os valores antes de entregar.

## 1. Problema

Cada relato validado precisa ser redigitado em outro sistema, com anexo, e o número da ordem de serviço precisa voltar ao Zela. Sem isso, o cidadão não vê o status "Encaminhado" e a triagem perde o rastreio.

## 2. Opções avaliadas

| Opção | Como funciona | Prós | Contras |
| --- | --- | --- | --- |
| **A. Manual** (As-Is) | Pessoa copia do painel para o portal | Zero investimento | Lento, erro de digitação, número da OS se perde |
| **B. RPA (UiPath)** | Robô lê `GET /robo/reports`, preenche o portal pela interface e grava a OS | Funciona com portal **sem API**. Rápido de construir. Log de cada execução | Quebra se o layout mudar. Precisa de máquina com o robô. Licença ao escalar |
| **C. Integração por API** | A API do Zela chama a API do sistema de destino | Mais estável e barata de manter. Sem máquina dedicada | Só existe se o destino tiver API **e** autorizar o acesso |

**Recomendação:** C, se a prova curta encontrar uma API autorizada. Caso contrário, B no portal de demonstração, com a limitação declarada. O robô já usa a API do lado do Zela, então só o lado do portal é feito por interface.

## 3. Estimativa de ganho (a medir)

| Item | Manual (estimativa) | Robô (estimativa) |
| --- | --- | --- |
| Tempo por relato | 6 min (abrir, copiar 4 campos, anexar foto, copiar número, registrar) | 1 min de execução, sem pessoa |
| Erros de digitação | Ocasionais | Zero nos campos copiados |
| Relatos sem número de OS no Zela | Frequentes (anotação à parte) | Zero. O PATCH é parte do fluxo |

Para **N** relatos por semana, a economia é de cerca de **5 × N minutos de equipe**. No volume do piloto (dezenas por semana) o ganho de tempo é pequeno. O valor maior está em **rastreabilidade e status para o cidadão**, que é o que sustenta o uso do produto.

## 4. Custos

| Item | Custo no MVP | Ao escalar |
| --- | --- | --- |
| UiPath Studio + Robot | Edição Community, gratuita para uso educacional | Licença paga de Robot/Orchestrator |
| Máquina para o robô | Computador da equipe | VM ou robô na nuvem |
| Construção | Horas da equipe (estimar) | Manutenção quando o portal mudar |
| Opção C (API) | Horas de desenvolvimento na API do Zela | Baixo |

## 5. Indicadores de sucesso

- % de relatos em triagem encaminhados pelo robô sem intervenção.
- Tempo médio de `em_triagem` até `encaminhado`. A DAG do Airflow pode medir isso quando registrar a data de cada mudança de status.
- Falhas por execução e motivo (log do robô).

## 6. Decisão

| Data | Resultado da prova curta | Opção escolhida | Justificativa |
| --- | --- | --- | --- |
| *(preencher)* | | | |
