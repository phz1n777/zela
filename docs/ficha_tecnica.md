# Ficha técnica comum

A mesma ficha vale para todas as disciplinas. Os PDFs, vídeos e prints de cada uma devem apontar para a mesma URL, o mesmo repositório e esta ficha.

| Campo | Conteúdo |
| --- | --- |
| Nome do produto | Zela: Zeladoria Urbana por Foto (nome provisório) |
| Cidadão e território | Quem circula a pé, de bicicleta, de carro ou em cadeira de rodas pelo bairro Jardim das Belezas, onde mora um dos integrantes (território piloto) |
| Problema, em uma frase | Danos na via ficam sem relato claro porque as pessoas não sabem onde relatar, o que informar ou se o problema já foi encaminhado |
| Proposta de valor | Transformar uma foto e um local em uma ocorrência estruturada e acompanhável |
| Arquitetura: componentes | App web (PWA) · API FastAPI · Visão (YOLO11n) · SQLite/Postgres · Airflow · Robô UiPath · FonteBot (GenAI) · Placa com QR (Maker Lab) · Docker, Terraform e GitHub Actions |
| Fontes de dados | Relatos enviados no piloto · fotos locais para avaliar o modelo · RDD2022 (CC BY 4.0) como ponto de partida do treino · registros simulados marcados com `source = demo` |
| Modelos de IA utilizados | YOLO11n ajustado no RDD2022 (sugestão de "dano na pista", sempre com confirmação humana) · LLM do FonteBot via OpenRouter (`nvidia/nemotron-3.5-super-vl:free`, com fallback) para dúvidas de uso |
| URL do MVP e repositório | https://ca-zela-uylmp.jollyglacier-50c67627.spaincentral.azurecontainerapps.io · https://github.com/phz1n777/zela |
| Indicadores de impacto | Relatos registrados por semana · % de sugestões confirmadas pelo cidadão · tempo do relato ao encaminhamento · ocorrências por status |
| ODS conectados | **11** (cidades sustentáveis): manutenção urbana mais visível e acompanhável · **9** (infraestrutura): dados para priorizar o reparo de vias · **13** (clima): base para, no futuro, mapear pontos de alagamento ligados a danos na drenagem, fora do MVP |

## Integrantes

| Nome | RM | Disciplinas sob responsabilidade |
| --- | --- | --- |
| Pedro Henrique de Assumção Lima | RM552746 | GenAI · BI & Startup · RPA · app e API · DevSecOps *(confirmar)* |
| Joseh Gabriel Trimboli Agra | RM553094 | GenAI · Big Data · Visão Computacional · RPA (robótica) |

Maker Lab ainda sem responsável definido.
