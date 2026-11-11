"""Baixa partes do RDD2022 e converte para o formato YOLO.

O RDD2022 é um único zip de 13 GB no figshare (CC BY 4.0), com um zip por
país dentro dele. Este script lê só os trechos dos países escolhidos usando
HTTP Range, sem baixar o arquivo inteiro.

Uso:
    python rdd_para_yolo.py --saida datasets/rdd --paises Czech China_MotorBike
"""

import argparse
import io
import random
import shutil
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

URL_RDD2022 = "https://ndownloader.figshare.com/files/38030910"

# Classes que o Zela usa. As demais do RDD2022 (D43, D44, D50, Repair...) são ignoradas.
CLASSES = ["D00", "D10", "D20", "D40"]
NOMES = {
    "D00": "rachadura_longitudinal",
    "D10": "rachadura_transversal",
    "D20": "rachadura_jacare",
    "D40": "buraco",
}


class ArquivoHttp(io.RawIOBase):
    """Arquivo remoto que lê só os bytes pedidos (HTTP Range)."""

    def __init__(self, url: str):
        req = urllib.request.Request(url, headers={"Range": "bytes=0-0"})
        with urllib.request.urlopen(req) as r:
            self.url = r.url  # URL final, depois dos redirecionamentos
            self.tamanho = int(r.headers["Content-Range"].split("/")[1])
        self.pos = 0

    def readable(self):
        return True

    def seekable(self):
        return True

    def tell(self):
        return self.pos

    def seek(self, deslocamento, origem=0):
        base = {0: 0, 1: self.pos, 2: self.tamanho}[origem]
        self.pos = base + deslocamento
        return self.pos

    def readinto(self, buffer):
        if self.pos >= self.tamanho or len(buffer) == 0:
            return 0
        fim = min(self.pos + len(buffer), self.tamanho) - 1
        req = urllib.request.Request(self.url, headers={"Range": f"bytes={self.pos}-{fim}"})
        with urllib.request.urlopen(req) as r:
            dados = r.read()
        buffer[: len(dados)] = dados
        self.pos += len(dados)
        return len(dados)


def baixar_paises(paises: list[str], pasta: Path) -> list[Path]:
    pasta.mkdir(parents=True, exist_ok=True)
    remoto = zipfile.ZipFile(io.BufferedReader(ArquivoHttp(URL_RDD2022), buffer_size=8 << 20))
    baixados = []
    for pais in paises:
        destino = pasta / f"{pais}.zip"
        if not destino.exists():
            membro = f"RDD2022/{pais}.zip"
            tamanho = remoto.getinfo(membro).compress_size / 1e6
            print(f"Baixando {membro} ({tamanho:.0f} MB)...")
            with remoto.open(membro) as origem, open(destino, "wb") as saida:
                shutil.copyfileobj(origem, saida, length=8 << 20)
        baixados.append(destino)
    return baixados


def voc_para_yolo(xml_path: Path, imagem: Path | None = None) -> list[str]:
    raiz = ET.parse(xml_path).getroot()
    largura = float(raiz.findtext("size/width") or 0)
    altura = float(raiz.findtext("size/height") or 0)
    if not largura or not altura:
        # Alguns XMLs vêm sem o tamanho; lemos da própria imagem.
        from PIL import Image

        with Image.open(imagem) as im:
            largura, altura = im.size
    linhas = []
    for obj in raiz.iter("object"):
        nome = obj.findtext("name")
        if nome not in CLASSES:
            continue
        caixa = obj.find("bndbox")
        x1, y1, x2, y2 = (float(caixa.findtext(k)) for k in ("xmin", "ymin", "xmax", "ymax"))
        if x2 <= x1 or y2 <= y1:
            continue
        cx, cy = (x1 + x2) / 2 / largura, (y1 + y2) / 2 / altura
        w, h = (x2 - x1) / largura, (y2 - y1) / altura
        linhas.append(f"{CLASSES.index(nome)} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}")
    return linhas


def montar_dataset(zips: list[Path], saida: Path, fracao_val: float, semente: int) -> Path:
    bruto = saida / "bruto"
    for z in zips:
        alvo = bruto / z.stem
        if not alvo.exists():
            print(f"Extraindo {z.name}...")
            with zipfile.ZipFile(z) as arquivo:
                arquivo.extractall(alvo)

    # Só a pasta train do RDD2022 tem anotações; o test oficial não tem.
    pares = []
    for xml in bruto.rglob("*.xml"):
        if "train" not in xml.parts:
            continue
        imagens = list(xml.parent.parent.parent.glob(f"images/{xml.stem}.jpg"))
        if imagens:
            pares.append((imagens[0], xml))
    if not pares:
        raise SystemExit("Nenhum par imagem + anotação encontrado. Confira a estrutura extraída.")

    random.Random(semente).shuffle(pares)
    n_val = int(len(pares) * fracao_val)
    divisoes = {"val": pares[:n_val], "train": pares[n_val:]}

    for divisao, itens in divisoes.items():
        (saida / "images" / divisao).mkdir(parents=True, exist_ok=True)
        (saida / "labels" / divisao).mkdir(parents=True, exist_ok=True)
        for imagem, xml in itens:
            shutil.copy(imagem, saida / "images" / divisao / imagem.name)
            rotulos = voc_para_yolo(xml, imagem)
            (saida / "labels" / divisao / f"{imagem.stem}.txt").write_text("\n".join(rotulos))
        print(f"{divisao}: {len(itens)} imagens")

    yaml = saida / "rdd.yaml"
    nomes = "\n".join(f"  {i}: {NOMES[c]}" for i, c in enumerate(CLASSES))
    yaml.write_text(f"path: {saida.resolve()}\ntrain: images/train\nval: images/val\nnames:\n{nomes}\n")
    return yaml


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--saida", default="datasets/rdd", type=Path)
    p.add_argument("--paises", nargs="+", default=["Czech", "China_MotorBike"])
    p.add_argument("--fracao-val", default=0.15, type=float)
    p.add_argument("--semente", default=42, type=int)
    args = p.parse_args()
    zips = baixar_paises(args.paises, args.saida / "zips")
    yaml = montar_dataset(zips, args.saida, args.fracao_val, args.semente)
    print(f"Dataset pronto: {yaml}")


if __name__ == "__main__":
    main()
