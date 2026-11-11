# vision — Applied Computer Vision

O modelo sugere se a foto do cidadão mostra **dano na pista** (buraco ou rachadura) e com qual confiança. A pessoa confirma ou corrige a sugestão. O modelo não decide se a via é segura.

O modelo é treinado com 4 classes do RDD2022, mas o produto apresenta uma única categoria automática: dano na pista. Lixo, bueiros e calçadas são registrados por categoria manual, e não dizemos que o modelo os cobre.

| Item | Escolha |
| --- | --- |
| Modelo | YOLO11n (Ultralytics), pré-treinado no COCO e ajustado no RDD2022 |
| Dataset | [RDD2022](https://doi.org/10.6084/m9.figshare.21431547.v1), CC BY 4.0, partes Czech e China_MotorBike (cerca de 450 MB) |
| Classes | `rachadura_longitudinal` (D00), `rachadura_transversal` (D10), `rachadura_jacare` (D20), `buraco` (D40) |
| Fora do modelo | Bueiro entupido e lixo: não há dataset público adequado, então o cidadão escolhe a categoria no app |

## Como treinar (Google Colab, GPU gratuita)

1. Abra o [colab.research.google.com](https://colab.research.google.com) e use **Arquivo → Fazer upload de notebook** com o [`treino_colab.ipynb`](treino_colab.ipynb).
2. Troque o ambiente para **GPU T4** e use **Executar tudo**. Leva cerca de 30 a 60 minutos.
3. O navegador baixa `zela_visao.zip`. Coloque o `best.pt` em `vision/modelos/` e descompacte o resto em `vision/resultados/`.
4. Para a API usar o modelo: `COM_VISAO=1 docker compose up --build`.

O notebook é gerado a partir dos scripts desta pasta. Depois de editar um `.py`, rode `python gerar_notebook.py`.

## Arquivos

| Arquivo | O que faz |
| --- | --- |
| [`rdd_para_yolo.py`](rdd_para_yolo.py) | Baixa só os países escolhidos de dentro do zip de 13 GB (HTTP Range) e converte as anotações Pascal VOC para o formato YOLO, com 85% para treino e 15% para validação |
| [`transformacoes.py`](transformacoes.py) | Salva cada etapa do processamento de uma foto e um painel com todas, mais as detecções em JSON |
| [`gerar_notebook.py`](gerar_notebook.py) | Monta o `treino_colab.ipynb` |
| [`../api/app/services/vision.py`](../api/app/services/vision.py) | Inferência na API e sugestão de `dano_na_pista` |

## Transformações intermediárias (para o PDF da disciplina)

| Etapa | Por quê |
| --- | --- |
| 1. Original | Foto como o cidadão enviou |
| 2. Redimensionada para 640 px com borda (letterbox) | Tamanho de entrada do YOLO, sem distorcer a proporção |
| 3. Escala de cinza | Dano no asfalto é questão de forma e textura, não de cor |
| 4. Contraste CLAHE | Realça rachaduras em asfalto escuro ou com sombra |
| 5. Desfoque gaussiano | Tira o ruído da textura do asfalto antes de procurar bordas |
| 6. Bordas (Canny) | Destaca o contorno de rachaduras e buracos |
| 7. Fechamento morfológico | Junta bordas próximas e forma o contorno contínuo do dano |
| 8. Detecção YOLO | Caixas, classe e confiança de cada dano |

As etapas 3 a 7 servem para explicar e visualizar o processamento. O YOLO recebe a imagem da etapa 2 em cores e aprende os próprios filtros.

## Dados extraídos de cada foto

A API grava três campos em cada relato:

- **`cv_label`:** `dano_na_pista` quando há pelo menos uma detecção de buraco ou rachadura com confiança de 0,25 ou mais. Sem isso, `sem_deteccao`. Fica nulo quando o modelo não está disponível.
- **`cv_confidence`:** a maior confiança entre as detecções válidas.
- **`cv_model`:** o nome do modelo (`VISION_MODEL_NAME`, ou o nome do arquivo `.pt`).

A API não calcula gravidade, porque o MVP não promete severidade. As caixas e as classes detalhadas de cada foto ficam no JSON gerado por `transformacoes.py`, para o relatório da disciplina. O limiar de 0,25 é um ponto de partida e precisa ser calibrado com as fotos locais do piloto.

## Avaliação local

Além das métricas no RDD2022, avaliar o modelo com fotos próprias do piloto, sem rostos nem placas. O resultado do piloto não prova que o modelo generaliza.

## Métricas

_Preencher com o `metricas.json` gerado pelo notebook (mAP50, mAP50-95, precisão, recall e mAP50 por classe)._
