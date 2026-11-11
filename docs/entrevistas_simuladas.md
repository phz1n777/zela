# Entrevistas simuladas (validação de hipóteses)

> **SIMULAÇÃO.** As entrevistas abaixo são **fictícias**, criadas com autorização do professor de BI & Startup Development (conversa de 10/11/2026) para exercitar a validação do Lean Canvas no prazo da GS. Os nomes são inventados e **não representam pessoas reais**. As respostas seguem o [roteiro de entrevistas](roteiro_entrevistas.md) e trazem objeções de propósito, para não confirmar tudo. No pitch e no PDF elas aparecem como "entrevistas simuladas", nunca como clientes ou tração.

## Perfis

| # | Perfil (fictício) | Território | Papel no modelo |
| --- | --- | --- | --- |
| E1 | "Marta", coordenadora de facilities de um campus universitário | Campus com ~8 mil pessoas por dia | Comprador |
| E2 | "Rogério", síndico profissional de um condomínio horizontal | Condomínio com 320 casas e ruas internas | Comprador |
| E3 | "Luciana", gerente de operações de um parque empresarial | 14 prédios, vias internas e estacionamentos | Comprador |
| E4 | "Caio", estudante que usa cadeira de rodas e circula pelo campus | Campus de E1 | Usuário (cidadão) |

## E1 · Coordenadora de facilities de campus

1. **Como chegam os avisos hoje?** "Por e-mail da manutenção, por um formulário antigo da intranet que quase ninguém usa e, principalmente, por WhatsApp de funcionário. Aluno quase nunca avisa."
2. **Última vez?** "Teve um buraco perto do estacionamento B. Chegaram três mensagens diferentes, sem foto, e a equipe foi duas vezes ao lugar errado."
3. **O mais trabalhoso?** "Achar o local exato e saber se já foi pedido. A gente abre chamado duplicado."
4. **Tempo por semana?** "Umas 3 a 4 horas de uma pessoa juntando e repassando os avisos."
5. **Presta contas?** "Para a diretoria, todo mês. Hoje monto a planilha na mão."
6. **Já tentou alguma ferramenta?** "Temos um sistema de chamados interno, mas ele é para funcionário logado. Aluno e visitante não entram."
7. **Vendo a demo:** "A foto com o local resolve o 'fomos ao lugar errado'. Mas eu precisaria que a OS caísse no nosso sistema de chamados, e não num portal separado."
8. **Quem decide e orçamento?** "Eu indico, mas quem aprova é a diretoria administrativa. Contrato anual, não mensal. Algo na faixa de R$ 400 a R$ 600 por mês passa se vier com o relatório mensal pronto."
9. **Piloto?** "Toparia 4 semanas num bloco, se não pedir login para o aluno."

## E2 · Síndico profissional de condomínio

1. **Como chegam os avisos?** "Grupo de WhatsApp dos moradores. Reclamam de tudo lá, misturado com festa e cachorro perdido."
2. **Última vez?** "Buraco na rua 4. Postaram foto no grupo, eu repassei ao zelador, e uma semana depois perguntaram de novo se alguém tinha visto."
3. **O mais trabalhoso?** "Responder que já foi pedido. Ninguém acompanha."
4. **Tempo por semana?** "Difícil dizer, uma hora por semana, espalhada."
5. **Presta contas?** "Na assembleia, e a cobrança é forte."
6. **Ferramenta?** "Uso um app de condomínio para reservas e boletos. Ele tem um 'fale com o síndico', mas ninguém usa para manutenção."
7. **Vendo a demo:** "Gostei do status 'Encaminhado', que é o que o morador quer ver. Não preciso do robô nem de portal: a manutenção sou eu e o zelador."
8. **Orçamento?** "R$ 400 por mês é caro para condomínio. A taxa já é alta. Algo entre R$ 150 e R$ 250 eu conseguiria aprovar em assembleia, ou como parte do app que já pago."
9. **Piloto?** "Gratuito, sim. Pago, só com aprovação da assembleia."

## E3 · Gerente de operações de parque empresarial

1. **Como chegam os avisos?** "Pelo help desk das empresas inquilinas e pela segurança patrimonial, por rádio."
2. **Última vez?** "Buraco na via de acesso de caminhões. Virou reclamação formal de um inquilino, porque danificou um pneu."
3. **O mais trabalhoso?** "Ter evidência: foto, data e prazo, por causa da responsabilidade civil."
4. **Tempo por semana?** "Pouco, porque o volume é baixo. O problema é o risco, não o tempo."
5. **Presta contas?** "Para o dono do empreendimento e para os inquilinos, com indicador de SLA."
6. **Ferramenta?** "Temos um sistema de manutenção corporativo, e ele tem API."
7. **Vendo a demo:** "A foto com hora e o histórico interessam muito, viram evidência. Mas, se o nosso sistema tem API, por que robô? Integração por API seria o certo."
8. **Orçamento?** "R$ 400 a R$ 800 por mês é pouco perto do custo de um sinistro. Mas exige contrato, LGPD bem explicada e quem responde se cair."
9. **Piloto?** "Talvez, depois de conversar com o jurídico."

## E4 · Estudante usuário de cadeira de rodas (cidadão)

1. **Já viu dano na via?** "Toda semana. Para mim, buraco perto de rampa é barreira, não incômodo."
2. **Já relatou?** "Uma vez, por e-mail à ouvidoria. Nunca tive resposta."
3. **Usaria o QR?** "Se abrir direto, sem cadastro, sim. Se pedir login ou um app para instalar, não."
4. **Vendo a demo:** "O botão grande e a confirmação estão bons. Senti falta de dizer que o buraco bloqueia a rampa, porque isso é mais urgente."
5. **O que faria voltar a usar?** "Ver que mudou de status. Se ficar parado, desisto."

## Síntese: o que as simulações sugerem

| Hipótese | Sinal nas simulações | Decisão |
| --- | --- | --- |
| **H1** Administração perde tempo com avisos informais | 3 de 3 compradores descrevem o problema (duplicidade, local errado, falta de status) | Mantida, com sinal **simulado** forte |
| **H2** Pagaria cerca de R$ 400/mês | **Misto.** Campus aceita R$ 400–600 em contrato anual. Parque aceita R$ 400–800. Condomínio só R$ 150–250 | **Preço por segmento:** R$ 400 para campus e parque, testar R$ 200 para condomínio |
| **H3** O cidadão relata se o QR abrir direto | E4 usaria **sem login e sem app**. E1 confirma que login afasta o aluno | Mantida. Reforça o "sem cadastro" |
| **H4** A sugestão da IA ajuda | Ninguém rejeitou. E4 pediu para marcar o bloqueio de acessibilidade | Mantida. Nova ideia: marcação "bloqueia rampa ou passagem" |
| **Nova:** encaminhamento | E1 e E3 querem a OS **no sistema que já usam**. E3 prefere API a RPA | O robô no portal de demonstração prova o fluxo. No produto real, priorizar integração (API quando houver, RPA quando não houver) |

**O que mudou no canvas:**
- **Segmentos:** campus e parque empresarial viram os early adopters. Condomínio passa a ser um segmento de preço menor.
- **Receita:** preço por segmento, em vez de um preço único.
- **Proposta de valor:** ganha "evidência com foto e histórico", vinda do parque.
- **Solução:** acessibilidade (bloqueio de rampa) entra como próximo passo.

**Limite:** isto é simulação. Antes de qualquer decisão real, as mesmas perguntas precisam ser feitas a pessoas reais.
