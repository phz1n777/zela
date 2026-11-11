"""Transformações intermediárias aplicadas a uma foto de denúncia.

A disciplina de Visão pede que o documento mostre cada etapa do
processamento. Este script salva uma imagem por etapa e um painel com todas.

Uso:
    python transformacoes.py foto.jpg --modelo best.pt --saida exemplos/
"""

import argparse
import json
from pathlib import Path

import cv2
import numpy as np

TAMANHO = 640


def letterbox(img: np.ndarray, tamanho: int = TAMANHO) -> np.ndarray:
    """Redimensiona mantendo a proporção e completa com cinza, como o YOLO faz."""
    h, w = img.shape[:2]
    escala = tamanho / max(h, w)
    nova = cv2.resize(img, (round(w * escala), round(h * escala)), interpolation=cv2.INTER_AREA)
    tela = np.full((tamanho, tamanho, 3), 114, dtype=np.uint8)
    y0, x0 = (tamanho - nova.shape[0]) // 2, (tamanho - nova.shape[1]) // 2
    tela[y0 : y0 + nova.shape[0], x0 : x0 + nova.shape[1]] = nova
    return tela


def etapas(img: np.ndarray) -> dict[str, np.ndarray]:
    """Cada etapa recebe a saída da anterior e devolve uma imagem para o relatório."""
    passos = {}
    passos["1_original"] = img
    redim = letterbox(img)
    passos["2_redimensionada_640"] = redim

    cinza = cv2.cvtColor(redim, cv2.COLOR_BGR2GRAY)
    passos["3_escala_de_cinza"] = cinza

    # CLAHE realça o contraste local: rachaduras em asfalto escuro aparecem melhor.
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(cinza)
    passos["4_contraste_clahe"] = clahe

    suave = cv2.GaussianBlur(clahe, (5, 5), 0)
    passos["5_desfoque_gaussiano"] = suave

    bordas = cv2.Canny(suave, 50, 150)
    passos["6_bordas_canny"] = bordas

    # Fechamento morfológico junta bordas próximas, formando o contorno do dano.
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    passos["7_morfologia_fechamento"] = cv2.morphologyEx(bordas, cv2.MORPH_CLOSE, kernel)
    return passos


def deteccoes(modelo_path: Path, img: np.ndarray):
    from ultralytics import YOLO

    resultado = YOLO(str(modelo_path)).predict(img, imgsz=TAMANHO, conf=0.25, verbose=False)[0]
    dados = [
        {
            "classe": resultado.names[int(c)],
            "confianca": round(float(p), 3),
            "caixa_xyxy": [round(float(v)) for v in xyxy],
        }
        for c, p, xyxy in zip(resultado.boxes.cls, resultado.boxes.conf, resultado.boxes.xyxy)
    ]
    return resultado.plot(), dados


def painel(passos: dict[str, np.ndarray], colunas: int = 4, lado: int = 320) -> np.ndarray:
    blocos = []
    for nome, im in passos.items():
        if im.ndim == 2:
            im = cv2.cvtColor(im, cv2.COLOR_GRAY2BGR)
        im = cv2.resize(letterbox(im), (lado, lado))
        cv2.putText(im, nome, (8, 22), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
        blocos.append(im)
    while len(blocos) % colunas:
        blocos.append(np.zeros_like(blocos[0]))
    linhas = [np.hstack(blocos[i : i + colunas]) for i in range(0, len(blocos), colunas)]
    return np.vstack(linhas)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("imagem", type=Path)
    p.add_argument("--modelo", type=Path)
    p.add_argument("--saida", type=Path, default=Path("exemplos"))
    args = p.parse_args()

    img = cv2.imread(str(args.imagem))
    if img is None:
        raise SystemExit(f"Não consegui abrir {args.imagem}")
    passos = etapas(img)
    if args.modelo:
        anotada, dados = deteccoes(args.modelo, img)
        passos["8_deteccao_yolo"] = anotada
    else:
        dados = []

    pasta = args.saida / args.imagem.stem
    pasta.mkdir(parents=True, exist_ok=True)
    for nome, im in passos.items():
        cv2.imwrite(str(pasta / f"{nome}.jpg"), im)
    cv2.imwrite(str(pasta / "painel.jpg"), painel(passos))
    (pasta / "deteccoes.json").write_text(json.dumps(dados, indent=2, ensure_ascii=False))
    print(f"{len(passos)} etapas salvas em {pasta}; {len(dados)} danos detectados")


if __name__ == "__main__":
    main()
