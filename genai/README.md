# FonteBot — Generative AI for Engineering (GS 2026.2)

Assistente de dúvidas do **Zeladoria Urbana por Foto**. Responde como usar o serviço com base somente em `FAQ.md`, devolve JSON validado e não inventa status, prazo ou diagnóstico da via.

Dupla: Pedro Henrique de Assumção Lima (RM552746) · Joseh Gabriel Trimboli Agra (RM553094)

## Arquivos
| Arquivo | Conteúdo |
|---|---|
| `fontebot_gs.ipynb` | Notebook da Aula 09.1 (OpenRouter: Gateway Multi-Modelo) usado como base, com o modelo trocado e a seção FonteBot da dupla. Mudanças marcadas com `# MODIFICACAO-ALUNO` / `## Modificação do aluno` |
| `FAQ.md` | Base documental (seções `FAQ-01` a `FAQ-14`) |
| `requirements.txt` | Dependências |
| `.env.example` | Modelo de variáveis de ambiente (sem segredo) |

## Como executar
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env    # preencha OPENROUTER_API_KEY
jupyter notebook
```
Execute todas as células (Kernel → Restart & Run All) e salve o notebook **com as saídas visíveis**. Uma execução completa usa cerca de 15 a 20 requisições do FonteBot, mais 1 da parte original da Aula 09.1.

## O que foi modificado
0. **Notebook-base:** `atividade.ipynb` da Aula 09.1, que usava `cohere/north-mini-code:free` sem temperatura definida. A troca de modelo foi feita na própria célula `MODELO_ESCOLHIDO`, e uma célula nova carrega a chave do `.env`.
1. **Modelo:** `nvidia/nemotron-3.5-super-vl:free`, com fallback automático pelo parâmetro `models` do OpenRouter (Gemma 4 31B e `openrouter/free`) e temperatura 0.2. A primeira escolha, `openai/gpt-oss-120b:free`, saiu do catálogo em 10/11/2026. A justificativa está no notebook.
2. **Três prompts revisados, com antes e depois:** base documental, ajuda de uso e saída JSON.
3. **Três experimentos:**
   - perguntas novas e caso sem resposta;
   - validação de JSON, offline e online;
   - erros de API (chave inválida, modelo inexistente e timeout).

## Saída
```json
{"intent": "como_relatar", "answer": "...", "needs_human": false, "sources": ["FAQ-03"]}
```

## Limitações e ética
Veja a última seção do notebook. Resumo:
- O bot só sabe o que está na FAQ e não consulta protocolos.
- Modelos gratuitos mudam e têm limite de requisições.
- A chave fica apenas em variável de ambiente.
- Não enviar dados pessoais nos testes.

## Resultados (execução de 10/11/2026)
O notebook está salvo com todas as saídas. Resumo:
- `needs_human` correto em 6 de 7 perguntas e nenhum prazo ou status inventado.
- JSON válido de primeira em 7 de 7 respostas, e validador offline com 9 de 9.
- Os 3 cenários de erro de API terminaram com a resposta segura de fallback.

Os detalhes estão na última célula do notebook.

## Evidências
| Arquivo | O que mostra |
|---|---|
| [`evidencias/fontebot_gs_executado.html`](evidencias/fontebot_gs_executado.html) | Notebook completo executado, para abrir no navegador |
| [`evidencias/01_modelo_e_chamada_base.png`](evidencias/01_modelo_e_chamada_base.png) | Troca de modelo na célula da aula, chamada real e justificativa |
| [`evidencias/02_experimento1_respostas.png`](evidencias/02_experimento1_respostas.png) | As 7 perguntas, com o JSON e o modelo que respondeu |
| [`evidencias/03_experimento1_resumo.png`](evidencias/03_experimento1_resumo.png) | Tabela `needs_human` e comparação com o prompt ingênuo |
| [`evidencias/04_experimento2_json.png`](evidencias/04_experimento2_json.png) | Validador offline (9/9) e qualidade do JSON nas chamadas reais |
| [`evidencias/05_experimento3_erros.png`](evidencias/05_experimento3_erros.png) | Chave inválida, modelo inexistente e timeout com fallback |
| [`evidencias/06_resultados_limitacoes_etica.png`](evidencias/06_resultados_limitacoes_etica.png) | Resultados, limitações e ética |

As imagens foram geradas a partir das saídas do notebook (nbconvert e Chrome headless), sem nenhuma edição.
