# docs: BI & Startup Development

**Entrega oficial** (prof. Henio Scheidt, até 19/11 às 23h55, um envio por equipe):
- **PDF único** com o Lean Canvas, o modelo de negócio e links clicáveis (vídeo, MVP, repositório).
- **Vídeo-pitch** de até 5 minutos, em link público, com todos os integrantes e demo do MVP.
- MVP em URL pública, repositório e ficha técnica.

**Rubrica (14 pontos):** Lean Canvas 2,0 · Modelo de negócio 2,5 · Narrativa 2,5 · Demo ponta a ponta 3,5 · Valor evidenciado 3,5.

## O PDF da entrega

[`entrega_bi/Zela_BI_Startup.pdf`](entrega_bi/Zela_BI_Startup.pdf) tem links, ficha técnica, o Lean Canvas no layout clássico de 9 blocos, a seção "o que mudou pelo caminho", o modelo de negócio, a conta e os limites. Para atualizar:

1. Preencha [`entrega_bi/links.json`](entrega_bi/links.json) com o vídeo, a URL do MVP, o repositório, o território e a equipe.
2. Preencha as linhas CP1, entrevistas e MVP da tabela "O que mudou" em [`entrega_bi/gerar_pdf.py`](entrega_bi/gerar_pdf.py). Atualize também o status dos blocos (⬜/🔶/✅) que forem validados.
3. Rode o script:

```bash
cd docs/entrega_bi && python3 gerar_pdf.py
```

Tudo que falta aparece em **vermelho** no PDF como `[preencher]`.

## Documentos de trabalho

| Documento | Conteúdo |
| --- | --- |
| [lean_canvas.md](lean_canvas.md) | Canvas com status e evidência por bloco, e o histórico desde o CP1 (a preencher) |
| [modelo_de_negocio.md](modelo_de_negocio.md) | Proposta de valor, receita e preço, a conta (custos × preço × territórios), canais, métricas e hipóteses |
| [roteiro_entrevistas.md](roteiro_entrevistas.md) | Conversas com compradores para validar as hipóteses H1 e H2 |
| [entrevistas_simuladas.md](entrevistas_simuladas.md) | 4 entrevistas **simuladas** (fictícias, autorizadas pelo professor) e a síntese do que mudou no canvas |
| [ficha_tecnica.md](ficha_tecnica.md) | Ficha técnica comum a todas as disciplinas |
| [roteiro_pitch.md](roteiro_pitch.md) | Os 6 blocos oficiais em 5 minutos, ligados à rubrica, com checklist de gravação |

**Para a equipe fazer:**
1. Trazer o canvas e as entrevistas do CP1 e dos MVPs anteriores. Isso vale pontos no critério do canvas.
2. Se der tempo, repetir as perguntas com pelo menos 1 comprador real. As simulações ficam como complemento.
3. Definir o território piloto.
4. Gravar o pitch.

Não apresentem preço, cliente ou tração que não estejam documentados.
