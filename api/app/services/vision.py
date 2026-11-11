"""Componente de Visão (Applied Computer Vision).

Usa o YOLO11n treinado no RDD2022 (ver vision/treino_colab.ipynb) para
sugerir se a foto mostra dano na pista (buraco ou rachadura).

O produto tem uma única categoria automática, `dano_na_pista`. As quatro
classes do modelo servem só para o treino e para o relatório da disciplina.
A sugestão sempre passa pela confirmação do cidadão e não diz se a via é segura.

Se o modelo não estiver disponível (variável VISION_MODEL_PATH vazia,
arquivo ausente ou pacote ultralytics não instalado), a API continua
funcionando sem sugestão, e o cidadão escolhe a categoria.
"""

import io
import logging
import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

log = logging.getLogger(__name__)

ROTULO_DANO = "dano_na_pista"
ROTULO_SEM_DANO = "sem_deteccao"

# Classes do modelo (vision/rdd_para_yolo.py) que contam como dano na pista.
CLASSES_DANO = {"buraco", "rachadura_jacare", "rachadura_longitudinal", "rachadura_transversal"}
CONFIANCA_MINIMA = 0.25


@dataclass
class Deteccao:
    classe: str
    confianca: float
    x1: float
    y1: float
    x2: float
    y2: float


@dataclass
class Sugestao:
    label: str | None  # dano_na_pista | sem_deteccao | None (sem modelo)
    confidence: float | None  # 0 a 1
    model: str | None


SEM_MODELO = Sugestao(label=None, confidence=None, model=None)


def nome_modelo() -> str:
    return os.getenv("VISION_MODEL_NAME") or Path(os.getenv("VISION_MODEL_PATH", "")).name or "desconhecido"


def avaliar(deteccoes: list[Deteccao], modelo: str) -> Sugestao:
    """Dano na pista quando há ao menos uma detecção confiável; a confiança é a maior delas."""
    validas = [d for d in deteccoes if d.confianca >= CONFIANCA_MINIMA and d.classe in CLASSES_DANO]
    if not validas:
        return Sugestao(label=ROTULO_SEM_DANO, confidence=0.0, model=modelo)
    melhor = max(validas, key=lambda d: d.confianca)
    return Sugestao(label=ROTULO_DANO, confidence=round(melhor.confianca, 3), model=modelo)


@lru_cache(maxsize=1)
def _carregar_modelo():
    caminho = os.getenv("VISION_MODEL_PATH", "")
    if not caminho or not Path(caminho).is_file():
        log.warning("Modelo de visão não encontrado (%r); sem sugestão automática", caminho)
        return None
    try:
        from ultralytics import YOLO
    except ImportError:
        log.warning("Pacote ultralytics não instalado; sem sugestão automática")
        return None
    return YOLO(caminho)


def detectar(modelo, imagem: bytes) -> list[Deteccao]:
    from PIL import Image

    with Image.open(io.BytesIO(imagem)) as im:
        im = im.convert("RGB")
        r = modelo.predict(im, imgsz=640, conf=CONFIANCA_MINIMA, verbose=False)[0]
    return [
        Deteccao(r.names[int(c)], float(p), *(float(v) for v in xyxy))
        for c, p, xyxy in zip(r.boxes.cls, r.boxes.conf, r.boxes.xyxy)
    ]


def sugerir(imagem: bytes) -> Sugestao:
    modelo = _carregar_modelo()
    if modelo is None:
        return SEM_MODELO
    try:
        dets = detectar(modelo, imagem)
    except Exception:  # foto corrompida não pode derrubar o relato
        log.exception("Falha na inferência de visão")
        return SEM_MODELO
    return avaliar(dets, nome_modelo())
