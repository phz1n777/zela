# Lean Canvas consolidado: Zela (Zeladoria Urbana por Foto)

> Versão da GS (11/2026). A rubrica avalia os **9 blocos com o que foi validado desde o CP1 e o que mudou pelo caminho**. Por isso cada bloco tem um **status** e a **evidência**. Preencham o histórico abaixo com o material dos checkpoints anteriores (canvas, entrevistas, MVP 0). Onde não houver evidência, o status fica como hipótese.

**Legenda de status:** ✅ validado (com evidência citada) · 🔶 parcialmente validado · ⬜ hipótese. **(sim.)** indica que o sinal vem das [entrevistas simuladas](entrevistas_simuladas.md), autorizadas pelo professor, e não de pessoas reais.

| # | Bloco | Conteúdo | Status | Evidência |
| --- | --- | --- | --- | --- |
| 1 | **Problema** | 1. Quem circula pelo território encontra danos na via e não sabe onde relatar nem o que informar. 2. Os relatos chegam dispersos, sem foto, local ou categoria. 3. Quem relatou não sabe se foi encaminhado. | 🔶 (sim.) | 3 de 3 compradores simulados descrevem duplicidade, local errado e falta de status ([E1–E3](entrevistas_simuladas.md)) |
| | *Alternativas atuais* | SP156 (telefone, site, app), grupos de WhatsApp, e-mail para a administração, redes sociais. | ⬜ | |
| 2 | **Segmentos de clientes** | **Usuário (não paga):** quem circula a pé, de bicicleta, de carro ou em cadeira de rodas pela região piloto. **Comprador:** administração de campus e de parque empresarial (preço cheio), condomínio grande (preço menor) e, depois, subprefeitura. | 🔶 (sim.) | Simulações: campus e parque aceitam a faixa de R$ 400; condomínio só R$ 150–250 |
| | *Early adopters* | Facilities de campus que presta contas mensalmente à diretoria. | 🔶 (sim.) | E1 aceita piloto de 4 semanas sem login para o aluno |
| 3 | **Proposta única de valor** | "Fotografe o dano, confirme a sugestão e acompanhe o encaminhamento." Para quem administra: uma fila única com foto, local, status e **histórico que serve de evidência**. | 🔶 | O fluxo funciona no MVP (demo). Nas simulações: o cidadão quer ver o status (E2, E4) e o parque quer evidência (E3) |
| | *Conceito de alto nível* | Um "protocolo com foto" para a zeladoria do território. | | |
| 4 | **Solução** | Formulário web sem cadastro aberto por QR · visão que sugere "dano na pista" com confirmação humana · painel de triagem · robô que abre a ordem de serviço · indicadores por período. | ✅ (técnica) | MVP ponta a ponta na URL pública · 32 testes automatizados · DAG executada · robô no portal de demonstração |
| 5 | **Canais** | Placas com QR nos pontos do território (Maker Lab), comunicação interna, venda consultiva com piloto gratuito. | ⬜ | Teste de leitura do QR no local (Maker Lab) |
| 6 | **Fontes de receita** | Assinatura por território, paga pelo comprador, com **preço por segmento**: R$ 400/mês para campus e parque (contrato anual) e R$ 200/mês para condomínio. O cidadão nunca paga. | 🔶 (sim.) | E1: R$ 400–600 · E2: R$ 150–250 · E3: R$ 400–800 (simulados) |
| 7 | **Estrutura de custos** | Nuvem, domínio, placas, implantação e suporte, licença de RPA ao escalar, chamadas de IA. Valores na seção "A conta" do modelo de negócio. | 🔶 | Estimativa pela calculadora de preços da nuvem. Ainda não há fatura real |
| 8 | **Métricas-chave** | Relatos que chegam ao painel · % de sugestões confirmadas · tempo do relato até a OS · % descartados · leituras do QR por placa. | 🔶 | As métricas são calculadas pela DAG e pela API (`/metrics`). Faltam dados de piloto real |
| 9 | **Vantagem injusta** | Ainda **não há**. Candidato: o histórico de relatos com foto e local do território, que melhora o modelo de visão local. | ⬜ | Só existe depois do piloto |

## O que mudou desde o CP1

> **A preencher pela equipe** com o canvas e as entrevistas dos checkpoints anteriores. Exemplo de linha: "CP1: o comprador era o cidadão (app pago) → GS: o cidadão usa grátis e o comprador é a administração, porque nas entrevistas ninguém pagaria para relatar buraco."

| Checkpoint | O que acreditávamos | O que aprendemos (evidência) | O que mudou no canvas |
| --- | --- | --- | --- |
| CP1 | | | |
| Entrevistas **simuladas** (11/2026) | Um preço único de R$ 400 para qualquer território. RPA como integração padrão | Condomínio paga menos. Campus e parque querem a OS no sistema que já usam. Parque prefere API | Preço por segmento. Campus e parque como early adopters. Integração por API quando houver, RPA quando não houver. Acessibilidade como próximo passo |
| MVP 0 | | | |
| MVP 1 | | | |
| GS | IA "classifica e protocola" vários problemas na prefeitura | O dataset (RDD2022) só cobre dano na pista, e o portal oficial exige prova de viabilidade | Uma categoria automática com confirmação humana. Encaminhamento para fila de demonstração. Sem promessa de reparo |

A linha da GS já está preenchida porque é uma mudança documentada neste repositório: compare a proposta original com a revisada.

## Riscos principais

1. **Comprador:** a administração pode preferir continuar no WhatsApp. É o primeiro teste das conversas.
2. **Uso:** cidadãos podem não ler o QR. Vamos medir com as placas.
3. **Visão:** o RDD2022 não representa ruas brasileiras. A confirmação humana mitiga.
4. **Integração:** sem acesso ao portal oficial, o encaminhamento fica numa fila de demonstração, e isso está declarado.
