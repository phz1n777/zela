"""Gera relatos de DEMONSTRAÇÃO para o painel, o pitch e a DAG do Airflow.

Todos os registros saem com `source = "demo"` e a descrição começa com
"[demonstração]". As fotos são imagens sintéticas (asfalto cinza com uma
mancha escura), sem pessoas, rostos ou placas.

Uso (na pasta api/, com o mesmo DATABASE_URL e UPLOAD_DIR da API):
    python -m app.demo --quantidade 40
    python -m app.demo --apagar          # remove só os registros demo
"""

import argparse
import random
import secrets
import struct
import uuid
import zlib
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, select

from .db import Report, SessionLocal, init_db
from .main import UPLOAD_DIR

# Pontos fictícios do território piloto. Trocar pelos reais quando a região for definida.
LOCAIS = [
    "Rua das Acácias, 120 (em frente à escola)",
    "Rua das Acácias, 310",
    "Av. Central, 900 (ponto de ônibus)",
    "Av. Central, 1500 (faixa de pedestres)",
    "Travessa do Mercado, 45",
    "Rua Projetada 2, esquina com a Av. Central",
    "Praça da Matriz (lado da banca)",
    "Rua do Campus, portão 2",
    "Rua do Campus, estacionamento",
    "Alameda dos Ipês, 77",
]

DESCRICOES = {
    "dano_na_pista": ["buraco perto da guia", "buraco grande na faixa da direita", "asfalto rachado", "buraco com água acumulada"],
    "calcada": ["calçada quebrada perto da rampa", "piso solto na calçada"],
    "bueiro": ["boca de lobo sem grade", "bueiro entupido"],
    "lixo": ["entulho na calçada"],
    "iluminacao": ["poste apagado"],
    "outro": ["placa de trânsito caída"],
}
PESOS_CATEGORIA = {"dano_na_pista": 60, "calcada": 12, "bueiro": 10, "lixo": 8, "iluminacao": 6, "outro": 4}
PESOS_STATUS = {"recebido": 30, "em_triagem": 25, "encaminhado": 35, "descartado": 10}


def png_sintetico(rng: random.Random, largura: int = 160, altura: int = 120) -> bytes:
    """PNG cinza com uma elipse escura (o "buraco"), gerado sem bibliotecas externas."""
    cx, cy = rng.randint(50, 110), rng.randint(50, 80)
    rx, ry = rng.randint(18, 40), rng.randint(8, 18)
    base = rng.randint(95, 125)
    linhas = bytearray()
    for y in range(altura):
        linhas.append(0)  # filtro "none"
        for x in range(largura):
            dentro = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1
            v = 35 if dentro else base + rng.randint(-12, 12)
            linhas += bytes((v, v, v))

    def bloco(tipo: bytes, dados: bytes) -> bytes:
        return struct.pack(">I", len(dados)) + tipo + dados + struct.pack(">I", zlib.crc32(tipo + dados))

    cabecalho = struct.pack(">IIBBBBB", largura, altura, 8, 2, 0, 0, 0)
    return b"\x89PNG\r\n\x1a\n" + bloco(b"IHDR", cabecalho) + bloco(b"IDAT", zlib.compress(bytes(linhas))) + bloco(b"IEND", b"")


def sortear(rng: random.Random, pesos: dict[str, int]) -> str:
    return rng.choices(list(pesos), weights=list(pesos.values()))[0]


def gerar(quantidade: int, semente: int, dias: int = 45) -> int:
    rng = random.Random(semente)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    agora = datetime.now(timezone.utc)
    with SessionLocal() as db:
        for i in range(quantidade):
            categoria = sortear(rng, PESOS_CATEGORIA)
            status = sortear(rng, PESOS_STATUS)
            nome = f"demo-{uuid.uuid4().hex}.png"
            (UPLOAD_DIR / nome).write_bytes(png_sintetico(rng))

            if categoria == "dano_na_pista":
                # Na maioria das fotos de buraco o modelo acerta; em algumas, não detecta.
                cv_label = "dano_na_pista" if rng.random() < 0.85 else "sem_deteccao"
            else:
                cv_label = "sem_deteccao" if rng.random() < 0.9 else "dano_na_pista"
            confianca = round(rng.uniform(0.35, 0.95), 3) if cv_label == "dano_na_pista" else 0.0

            db.add(Report(
                created_at=agora - timedelta(days=rng.uniform(0, dias)),
                location=rng.choice(LOCAIS),
                description=f"[demonstração] {rng.choice(DESCRICOES[categoria])}",
                image=nome,
                category=categoria,
                status=status,
                source="demo",
                cv_label=cv_label,
                cv_confidence=confianca,
                cv_model="demo-simulado",
                cv_reviewed=status != "recebido" or rng.random() < 0.7,
                service_order=f"OS-DEMO-{i + 1:04d}" if status == "encaminhado" else None,
                confirm_token=secrets.token_urlsafe(24),
            ))
        db.commit()
    return quantidade


def apagar() -> int:
    with SessionLocal() as db:
        nomes = db.scalars(select(Report.image).where(Report.source == "demo")).all()
        db.execute(delete(Report).where(Report.source == "demo"))
        db.commit()
    for nome in nomes:
        (UPLOAD_DIR / nome).unlink(missing_ok=True)
    return len(nomes)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--quantidade", type=int, default=40)
    p.add_argument("--semente", type=int, default=2026, help="mesma semente, mesmos dados")
    p.add_argument("--apagar", action="store_true", help="remove os registros demo e as fotos deles")
    args = p.parse_args()
    init_db()
    if args.apagar:
        print(f"{apagar()} relatos demo removidos.")
    else:
        print(f"{gerar(args.quantidade, args.semente)} relatos demo criados (source=demo).")


if __name__ == "__main__":
    main()
