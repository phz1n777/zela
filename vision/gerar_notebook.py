"""Gera treino_colab.ipynb a partir dos scripts desta pasta.

Os scripts entram no notebook como células %%writefile, então só existe uma
cópia do código: edite os .py e rode `python gerar_notebook.py` de novo.
"""

import json
from pathlib import Path

AQUI = Path(__file__).parent


def md(texto):
    return {"cell_type": "markdown", "metadata": {}, "source": texto.strip()}


def code(texto):
    return {
        "cell_type": "code",
        "metadata": {},
        "execution_count": None,
        "outputs": [],
        "source": texto.strip(),
    }


def arquivo(nome):
    return code(f"%%writefile {nome}\n" + (AQUI / nome).read_text())


celulas = [
    md("""
# Zela: treino do modelo de Visão (YOLO11n + RDD2022)

1. Menu **Ambiente de execução → Alterar o tipo de ambiente → GPU T4**.
2. **Ambiente de execução → Executar tudo**. Leva cerca de 30 a 60 minutos.
3. No fim, o navegador baixa `zela_visao.zip` com o `best.pt`, as métricas e as imagens das transformações.
4. Coloque o `best.pt` em `vision/modelos/` no repositório e descompacte o resto em `vision/resultados/`.

Dataset: [RDD2022](https://doi.org/10.6084/m9.figshare.21431547.v1) (CC BY 4.0), partes Czech e China_MotorBike.
"""),
    code("""
!pip -q install ultralytics
import torch
assert torch.cuda.is_available(), "Sem GPU: troque o tipo de ambiente para GPU T4"
print(torch.cuda.get_device_name(0))
"""),
    arquivo("rdd_para_yolo.py"),
    arquivo("transformacoes.py"),
    md("## 1. Baixar e converter o dataset (cerca de 450 MB)"),
    code("!python rdd_para_yolo.py --saida /content/datasets/rdd --paises Czech China_MotorBike"),
    md("## 2. Treinar"),
    code("""
from ultralytics import YOLO

modelo = YOLO("yolo11n.pt")  # pesos pré-treinados no COCO
modelo.train(
    data="/content/datasets/rdd/rdd.yaml",
    epochs=60,
    imgsz=640,
    batch=32,
    patience=15,  # para cedo se a validação parar de melhorar
    seed=42,
    project="/content/runs",
    name="zela",
    exist_ok=True,
)
"""),
    md("## 3. Avaliar"),
    code("""
import json
from pathlib import Path

melhor = YOLO("/content/runs/zela/weights/best.pt")
m = melhor.val(data="/content/datasets/rdd/rdd.yaml", imgsz=640, split="val")
metricas = {
    "mAP50": round(float(m.box.map50), 4),
    "mAP50-95": round(float(m.box.map), 4),
    "precisao": round(float(m.box.mp), 4),
    "recall": round(float(m.box.mr), 4),
    "mAP50_por_classe": {melhor.names[i]: round(float(v), 4) for i, v in enumerate(m.box.ap50)},
}
print(json.dumps(metricas, indent=2, ensure_ascii=False))
Path("/content/entrega").mkdir(exist_ok=True)
Path("/content/entrega/metricas.json").write_text(json.dumps(metricas, indent=2, ensure_ascii=False))
"""),
    md("## 4. Transformações intermediárias em 3 imagens de validação"),
    code("""
import random
imagens = sorted(Path("/content/datasets/rdd/images/val").glob("*.jpg"))
for img in random.Random(7).sample(imagens, 3):
    !python transformacoes.py {img} --modelo /content/runs/zela/weights/best.pt --saida /content/entrega/exemplos
"""),
    md("## 5. Empacotar e baixar"),
    code("""
import shutil
from google.colab import files

for nome in ["weights/best.pt", "results.png", "confusion_matrix.png", "BoxPR_curve.png"]:
    origem = Path("/content/runs/zela") / nome
    if origem.exists():
        shutil.copy(origem, "/content/entrega/")
shutil.make_archive("/content/zela_visao", "zip", "/content/entrega")
files.download("/content/zela_visao.zip")
"""),
]

nb = {
    "nbformat": 4,
    "nbformat_minor": 5,
    "metadata": {
        "accelerator": "GPU",
        "colab": {"provenance": [], "gpuType": "T4"},
        "kernelspec": {"name": "python3", "display_name": "Python 3"},
    },
    "cells": celulas,
}
(AQUI / "treino_colab.ipynb").write_text(json.dumps(nb, indent=1, ensure_ascii=False))
print("treino_colab.ipynb gerado")
