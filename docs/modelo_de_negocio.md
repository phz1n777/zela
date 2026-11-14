# Modelo de negócio

> Versão da GS (11/2026). Cobre o que a rubrica pede: **proposta de valor, fontes de receita e precificação, canais e métricas, e a conta que fecha**. Os números são **estimativas com premissas declaradas**. O preço é uma **hipótese a testar** nas conversas, não um preço confirmado.

## Quem é quem

| Papel | Quem | O que ganha | O que paga |
| --- | --- | --- | --- |
| **Usuário** | Quem circula pelo território: estudantes, funcionários, moradores, pessoas com mobilidade reduzida | Relatar em menos de 1 minuto, sem cadastro, e acompanhar o protocolo | Nada |
| **Comprador** | Administração do território: prefeitura de campus, síndico ou administradora de condomínio grande, gestor de parque empresarial | Fila única de ocorrências com foto, local e status, indicadores para prestar contas e menos retrabalho de triagem | Assinatura do painel |
| **Operador** | Equipe de zeladoria ou manutenção do comprador | Ordem de serviço já preenchida, sem redigitar | (incluso) |
| **Parceiro futuro** | Subprefeitura ou órgão municipal | Relatos mais completos chegando ao canal oficial | A definir. Fora do MVP |

## Proposta de valor

| Para quem | Antes | Com o Zela | Como mostramos |
| --- | --- | --- | --- |
| Cidadão | Não sabe onde relatar e nunca sabe se foi encaminhado | Foto, local e confirmação em menos de 1 minuto, com protocolo e status | Demo ao vivo e consulta do protocolo |
| Administração | Mensagens soltas, sem foto nem local, e redigitação no sistema de manutenção | Fila única com foto e local, triagem em um clique, OS aberta pelo robô | Painel e robô no portal de demonstração |
| Equipe de manutenção | Volta ao local para entender o problema | Foto e referência na própria OS | Anexo na OS do portal |

## Fontes de receita e preço

- **Modelo:** assinatura mensal **por território** (campus, condomínio, parque), paga pelo comprador. O cidadão nunca paga.
- **Implantação:** placas com QR e configuração inclusas no primeiro mês, ou cobradas à parte a partir do segundo território.
- **Preço por segmento** (ajustado depois das [entrevistas simuladas](entrevistas_simuladas.md)):
  - campus e parque empresarial: **R$ 400/mês**, em contrato anual;
  - condomínio: **R$ 200/mês**, porque na simulação o síndico só aprovaria R$ 150–250.
- A âncora de R$ 400 vem da conta abaixo: é o menor valor em que **1 território** cobre a infraestrutura e paga a implantação em menos de 3 meses. Com R$ 200, são 4 territórios para cobrir a nuvem e cerca de 8 meses para pagar a implantação. Por isso o condomínio entra como segundo segmento, e não como early adopter.
- **Tudo isso é hipótese:** o sinal vem de simulação, não de compradores reais.

## A conta (estimativa)

**Premissas** (ajustem se tiverem números melhores):
- US$ 1 = R$ 5,50.
- Hora da equipe (implantação e suporte) = R$ 60.
- Infraestrutura compartilhada entre todos os territórios: uma instância da API, um banco, um armazenamento.
- Custo da nuvem pela estimativa do ambiente publicado (Azure, região `spaincentral`), feita a partir de preços públicos. Ainda não há fatura real: conferir em *Cost Management + Billing*.

### Custo fixo mensal (compartilhado)

Valores da estimativa de nuvem em [custos_e_lgpd.md](custos_e_lgpd.md): **US$ 30 a 60 por mês** com o piloto ligado o tempo todo, no Azure (`spaincentral`).

| Item | Estimativa |
| --- | --- |
| Container App (0,5 vCPU, 1 GiB, réplica sempre ligada) | maior parcela variável |
| PostgreSQL Flexible B1ms + 32 GB | parcela fixa principal |
| Container Registry (Basic), logs e alerta | pequena |
| Domínio `.com.br` (~R$ 40/ano) | ~ R$ 4 |
| LLM do FonteBot (modelos gratuitos no MVP) | R$ 0 |
| **Total fixo** | **US$ 30–60 ≈ R$ 165–330/mês. Usamos R$ 250 (meio da faixa)** |

### Custo por território

| Item | Estimativa |
| --- | --- |
| Suporte e acompanhamento (2 h/mês × R$ 60) | R$ 120/mês |
| **Implantação, uma vez:** 6 placas × R$ 50 + 6 h de instalação e treinamento × R$ 60 | **R$ 660** |

### Resultado por cenário de preço

| Preço/mês | Margem por território (preço − R$ 120) | Territórios para cobrir o fixo (R$ 250; pior caso R$ 330) | Meses para pagar a implantação (R$ 660) |
| --- | --- | --- | --- |
| R$ 200 | R$ 80 | 4 (5 no pior caso) | ~8,3 |
| **R$ 400** | **R$ 280** | **1 (2 no pior caso)** | **~2,4** |
| R$ 800 | R$ 680 | 1 | ~1,0 |

**Leitura:** com R$ 400, **1 território cobre a nuvem** no cenário médio (R$ 250), e são 2 no pior caso (R$ 330). A implantação se paga em cerca de 2,4 meses. Com 5 territórios, a receita (R$ 2.000) contra o custo (R$ 250 + 5 × R$ 120 = R$ 850) deixa ~R$ 1.150/mês. A conta só fecha **se a hipótese de preço se confirmar**.

**O que pode quebrar a conta:**
- Suporte maior que 2 h/mês por território.
- Licença de RPA paga ao sair da edição Community.
- LLM pago se os modelos gratuitos ficarem indisponíveis.
- Volume de fotos muito maior que o previsto.

## Canais

1. **Piloto de uso** de 4 semanas no território piloto (o bairro Jardim das Belezas, onde mora um dos integrantes), para validar o cidadão: leituras do QR, relatos e tempo até a triagem. Em seguida, **piloto gratuito com um comprador** (campus ou parque empresarial), com autorização da administração.
2. **Placas com QR** nos pontos com mais problemas. É o canal de entrada do cidadão (Maker Lab).
3. **Venda consultiva**, levando o relatório do piloto, com os indicadores da DAG, ao próximo comprador.
4. **Futuro:** associações de bairro e subprefeituras, quando houver integração oficial.

## Métricas-chave

| Indicador | Cálculo | Fonte | Limite |
| --- | --- | --- | --- |
| Conclusão do fluxo | Relatos que chegam ao painel ÷ relatos iniciados | API e painel | Registrar falhas e abandono |
| Concordância da visão | Sugestões confirmadas ÷ fotos analisadas | DAG (`taxa_concordancia_visao`) | Amostra local pequena. Não alegar acurácia geral |
| Tempo de encaminhamento | Relato criado até a OS na fila | API (status) e portal | Não é tempo de reparo |
| Acesso à informação | Leituras do QR e relatos por placa | Teste de leitura no local | Validar com pessoas do território |
| Retenção do comprador | Territórios que continuam após o piloto | Contratos | Só existe depois do piloto |

## Hipóteses e como testar

| # | Hipótese | Como testar no prazo | Critério para manter |
| --- | --- | --- | --- |
| H1 | A administração recebe relatos por canais informais e perde tempo organizando | 3 a 5 conversas com o [roteiro de entrevistas](roteiro_entrevistas.md) | Pelo menos 3 confirmam o problema sem sugestão |
| H2 | Ela pagaria cerca de R$ 400/mês por território | Simulação: campus e parque sim, condomínio não (R$ 150–250) | Ajustada para preço por segmento. Confirmar com compradores reais |
| H3 | O cidadão relata se o QR estiver no lugar do problema | Placa do Maker Lab e contagem de relatos | Algum relato real vindo do QR |
| H4 | A sugestão automática ajuda e não atrapalha | Taxa de confirmação da visão | Mais confirmações do que correções nas fotos de buraco |

## O que não prometemos

- Reparo ou prazo de atendimento.
- Integração com o canal oficial da prefeitura antes da prova de viabilidade.
- Detecção automática de lixo, bueiros ou calçadas.
