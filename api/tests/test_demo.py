import os
import tempfile

TMP = tempfile.mkdtemp()
os.environ.setdefault("DATABASE_URL", f"sqlite:///{TMP}/teste.db")
os.environ.setdefault("UPLOAD_DIR", f"{TMP}/uploads")

import random  # noqa: E402

from sqlalchemy import select  # noqa: E402

from app import demo  # noqa: E402
from app.db import Report, SessionLocal, init_db  # noqa: E402


def test_png_sintetico_e_valido():
    png = demo.png_sintetico(random.Random(1))
    assert png.startswith(b"\x89PNG\r\n\x1a\n") and b"IEND" in png


def test_gera_e_apaga_so_demo():
    init_db()
    with SessionLocal() as db:
        db.add(Report(location="Rua real", image="x.png", category="outro", confirm_token="t"))
        db.commit()
    demo.gerar(12, semente=7)
    with SessionLocal() as db:
        demos = db.scalars(select(Report).where(Report.source == "demo")).all()
    assert len(demos) >= 12
    assert all(r.description.startswith("[demonstração]") for r in demos)
    assert all((r.service_order is not None) == (r.status == "encaminhado") for r in demos)
    assert all((demo.UPLOAD_DIR / r.image).is_file() for r in demos)

    demo.apagar()
    with SessionLocal() as db:
        restantes = db.scalars(select(Report)).all()
    assert all(r.source != "demo" for r in restantes)
    assert any(r.location == "Rua real" for r in restantes)
